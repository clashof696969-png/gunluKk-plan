import flet as ft
from datetime import datetime
import json
import time
import threading

def main(page: ft.Page):
    # --- Sayfa Ayarları ---
    page.title = "Günlük Planlayıcım"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = None 

    # --- Görsel Bileşenler ---
    ust_baslik = ft.Text("Bugünün Planı", size=28, weight="bold", color="blue")
    tarih_metni = ft.Text("", size=16, color="grey")
    saat_metni = ft.Text("", size=22, weight="bold", color="amber")
    
    gorevler_kutusu = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    
    # Görev için tarih seçme kutusu (Otomatik bugünü gösterir)
    gorev_tarihi_input = ft.TextField(
        value=datetime.now().strftime("%Y-%m-%d"), 
        label="Tarih", 
        width=120,
        text_align=ft.TextAlign.CENTER
    )
    
    yeni_gorev_input = ft.TextField(
        hint_text="Görev yazın...",
        expand=True,
    )

    # --- Fonksiyonlar ---
    def gorevleri_yukle():
        gorevler_kutusu.controls.clear()
        bugun = datetime.now().strftime("%Y-%m-%d")
        tarih_metni.value = bugun
        
        try:
            with open("gorevler.json.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            
        if bugun in data and len(data[bugun]) > 0:
            for gorev in data[bugun]:
                gorevler_kutusu.controls.append(ft.Text(f"• {gorev}", size=16))
        else:
            gorevler_kutusu.controls.append(
                ft.Text("Bugün için girilmiş bir görev bulunmuyor.", italic=True, color="grey")
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
        gorev_tarihi_input.value = datetime.now().strftime("%Y-%m-%d") 
        gorevleri_yukle()         

    # --- Buton ve Alt Satır Tasarımı (Düzeltilmiş Şık Metin Butonu) ---
    ekle_butonu = ft.ElevatedButton(
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
            su_an = datetime.now().strftime("%H:%M:%S")
            saat_metni.value = su_an
            try:
                page.update()
            except:
                pass
            time.sleep(1)

    saat_thread = threading.Thread(target=saati_guncelle, daemon=True)
    saat_thread.start()

# Önerilen modern başlatma yöntemiyle uyarı yazısını da sıfırladık
if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
