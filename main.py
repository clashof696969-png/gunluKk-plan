import flet as ft
import datetime
import json
import time
import threading

def main(page: ft.Page):
    page.title = "Günlük Planlayıcım"
    page.theme_mode = ft.ThemeMode.DARK  # Karanlık tema
    page.scroll = ft.ScrollMode.AUTO     # Ekran dolunca kaydırılabilmesi için
    
    # Görsel bileşenleri (Widget) önceden tanımlayalım
    ust_baslik = ft.Text("Bugünün Planı", size=28, weight="bold", color="blue")
    tarih_metni = ft.Text("", size=16, color="grey")
    saat_metni = ft.Text("", size=22, weight="bold", color="amber")
    
    # Görevlerin listeleneceği dikey sütun container'ı
    gorevler_kutusu = ft.Column()
    
    # Yeni görev ekleme kutusu ve butonu
    yeni_gorev_input = ft.TextField(
        hint_text="Yeni bir görev yazın...", 
        expand=True,
        border_radius=8
    )
    
    # Görevleri dosyadan yükleyen fonksiyon
    def gorevleri_yukle():
        gorevler_kutusu.controls.clear()
        
        bugun = datetime.datetime.now().strftime("%Y-%m-%d")
        tarih_metni.value = bugun
        
        # JSON dosyasını oku
        try:
            with open("gorevler.json.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
            
        bugunun_gorevleri = data.get(bugun, [])
        
        if bugunun_gorevleri:
            for gorev in bugunun_gorevleri:
                gorevler_kutusu.controls.append(
                    ft.Container(
                        content=ft.Checkbox(label=gorev, value=False, size=20),
                        padding=12,
                        margin=ft.margin.only(bottom=8),
                        bgcolor="white10",
                        border_radius=10
                    )
                )
        else:
            gorevler_kutusu.controls.append(
                ft.Text("Bugün için girilmiş bir görev bulunmuyor.", size=16, italic=True, color="grey")
            )
        page.update()

    # Görev ekleme butonuna basılınca çalışacak fonksiyon
    def gorev_ekle_click(e):
        if not yeni_gorev_input.value:
            return  # Boşsa bir şey yapma
            
        bugun = datetime.datetime.now().strftime("%Y-%m-%d")
        
        try:
            with open("gorevler.json.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
            
        if bugun not in data:
            data[bugun] = []
            
        # Yeni görevi listeye ekle
        data[bugun].append(yeni_gorev_input.value)
        
        # Dosyayı güncelle
        with open("gorevler.json.txt", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        yeni_gorev_input.value = ""  # Kutuyu temizle
        gorevleri_yukle()           # Listeyi yenile

    # Ekleme butonu tasarımı
	ekle_butonu = ft.IconButton(
	icon=ft.icons.ADD_CIRCLE_OUTLINE,
        icon_color=ft.colors.BLUE,
        icon_size=40,
        on_click=gorev_ekle_click
    )
    
    # Görev ekleme satırı (Yazı kutusu + Buton yan yana)
    ekleme_satiri = ft.Row(
        controls=[yeni_gorev_input, ekle_butonu],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Saati ve tarihi arka planda her saniye güncelleyen fonksiyon (Thread)
    def saati_guncelle():
        while True:
            try:
                simdi = datetime.datetime.now()
                saat_metni.value = simdi.strftime("%H:%M:%S")
                # Eğer gün değişirse tarihi de güncelle
                if tarih_metni.value != simdi.strftime("%Y-%m-%d"):
                    tarih_metni.value = simdi.strftime("%Y-%m-%d")
                page.update()
                time.sleep(1)
            except Exception:
                break  # Sayfa kapanırsa döngüden çık

    # Sayfaya bileşenleri ekleyelim
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([ust_baslik, saat_metni], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    tarih_metni,
                    ft.Divider(height=20, color="white24"),
                    ekleme_satiri,
                    ft.Divider(height=20, color="transparent"),
                    gorevler_kutusu
                ]
            ),
            padding=20
        )
    )

    # Arka plan saat güncelleyiciyi başlat
    saat_thread = threading.Thread(target=saati_guncelle, daemon=True)
    saat_thread.start()

    # İlk açılışta mevcut görevleri yükle
    gorevleri_yukle()

# Uygulamayı hem yerelde hem web formatında çalıştırmak için kararlı yapı
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)