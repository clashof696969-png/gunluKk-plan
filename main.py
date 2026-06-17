import flet as ft
from datetime import datetime, timedelta, timezone
import json
import time
import threading

def main(page: ft.Page):
    # --- Türkiye Saati Ayarı (UTC+3) ---
    TR_TZ = timezone(timedelta(hours=3))

    page.title = "Günlük Planlayıcım"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = None 

    # --- Görsel Bileşenler ---
    ust_baslik = ft.Text("Günlük Planlayıcım", size=28, weight="bold", color="blue")
    tarih_metni = ft.Text("", size=16, color="grey")
    saat_metni = ft.Text("", size=22, weight="bold", color="amber")
    
    gorevler_kutusu = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    
    # Tarih kutusundaki yazı değiştiğinde çalışacak fonksiyon
    def tarih_degisti(e):
        # Yalnızca format tam olarak tamamlandığında (örn: 2026-06-25) çalışır
        if len(gorev_tarihi_input.value) == 10:
            gorevleri_yukle(gorev_tarihi_input.value)

    gorev_tarihi_input = ft.TextField(
        value=datetime.now(TR_TZ).strftime("%Y-%m-%d"), 
        label="Tarih", 
        width=120,
        text_align=ft.TextAlign.CENTER,
        on_change=tarih_degisti
    )
    
    yeni_gorev_input = ft.TextField(
        hint_text="Görev yazın...",
        expand=True,
    )

    # --- Fonksiyonlar ---
    def gorevi_sil(e):
        # Hangi butona basıldığını ve içindeki bilgiyi alıyoruz
        tarih = e.control.data["tarih"]
        index = e.control.data["index"]
        
        try:
            with open("gorevler.json.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if tarih in data and len(data[tarih]) > index:
                data[tarih].pop(index) # Görevi listeden çıkart
                with open("gorevler.json.txt", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    
            gorevleri_yukle(tarih) # Sayfayı güncel tarihle yenile
        except Exception:
            pass

    def gorevleri_yukle(secilen_tarih=None):
        gorevler_kutusu.controls.clear()
        
        # Eğer tarih verilmemişse bugünü baz al
        if secilen_tarih is None:
            secilen_tarih = datetime.now(TR_TZ).strftime("%Y-%m-%d")
            
        tarih_metni.value = f"Gösterilen Tarih: {secilen_tarih}"
        
        try:
            with open("gorevler.json.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            
        if secilen_tarih in data and len(data[secilen_tarih]) > 0:
            for i, gorev in enumerate(data[secilen_tarih]):
                # Her görev için yan yana "Yazı + Sil Butonu" oluştur
                gorev_satiri = ft.Row(
                    controls=[
                        ft.Text(f"• {gorev}", size=16, expand=True),
                        ft.TextButton(
                            "Sil", 
                            icon="delete",
                            icon_color="red", 
                            data={"tarih": secilen_tarih, "index": i},
                            on_click=gorevi_sil
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
                gorevler_kutusu.controls.append(gorev_satiri)
        else:
            gorevler_kutusu.controls.append(
                ft.Text("Bu tarih için girilmiş bir görev bulunmuyor.", italic=True, color="grey")
            )
        page.update()

    def gorev_ekle_click(e):
        if not yeni_gorev_input.value or not gorev_tarihi_input.value:
            return  
            
        hedef_tarih = gorev_tarihi_input.value
        
        try:
            with open("gorevler.json.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            
        if hedef_tarih not in data:
            data[hedef_tarih] = []
            
        data[hedef_tarih].append(yeni_gorev_input.value)
        
        with open("gorevler.json.txt", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        yeni_gorev_input.value = "" 
        gorevleri_yukle(hedef_tarih)         

    ekle_butonu = ft.FilledButton(
        "Ekle",
        on_click=gorev_ekle_click
    )

    ekleme_satiri = ft.Row(
        controls=[gorev_tarihi_input, yeni_gorev_input, ekle_butonu],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # --- Sayfaya Yerleştirme ---
    page.add(
        ft.Row([ust_baslik, saat_metni], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        tarih_metni,
        ft.Divider(),
        gorevler_kutusu,  
        ft.Divider(),
        ekleme_satiri     
    )

    gorevleri_yukle()

    # --- Arka Planda Saati Güncelleyen Fonksiyon ---
    def saati_guncelle():
        while True:
            su_an = datetime.now(TR_TZ).strftime("%H:%M:%S")
            saat_metni.value = su_an
            try:
                page.update()
            except:
                pass
            time.sleep(1)

    saat_thread = threading.Thread(target=saati_guncelle, daemon=True)
    saat_thread.start()

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
