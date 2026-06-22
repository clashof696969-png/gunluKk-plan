import flet as ft
from datetime import datetime, timedelta, timezone
import requests
import uuid

BIN_ID = "6a385e06da38895dfee86ba1"
API_KEY = "$2a$10$cpHvssfY0MACNPlPaVA2cef4AzwXqq0wZeaTheUvNW8eIGnMIlbpO"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

def veri_cek():
    try:
        cevap = requests.get(URL, headers=HEADERS)
        if cevap.status_code == 200:
            veri = cevap.json().get("record", {})
            if "test" in veri: del veri["test"]
            return veri
    except: pass
    return {}

def veri_kaydet(veri):
    try: requests.put(URL, json=veri, headers=HEADERS)
    except: pass

def main(page: ft.Page):
    TR_TZ = timezone(timedelta(hours=3))
    page.title = "Kişisel Planlayıcı"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    aktif_kullanici_id = [""]
    aktif_kullanici_isim = [""]

    def tema_degistir(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.update()
        if aktif_kullanici_id[0]:
            gorevleri_yukle()

    kullanici_input = ft.TextField(label="İsminiz (Sadece ilk girişte sorulur)", width=300, text_align=ft.TextAlign.CENTER)
    uyari_metni = ft.Text("", color="red", size=14, weight="bold")

    def giris_yap_click(e):
        kadi = kullanici_input.value.strip()
        if not kadi:
            uyari_metni.value = "Lütfen bir isim girin!"
            page.update()
            return
        
        gizli_id = str(uuid.uuid4())
        try:
            if hasattr(page, "client_storage"):
                page.client_storage.set("gizli_id", gizli_id)
                page.client_storage.set("gorunen_isim", kadi)
        except: pass
        
        aktif_kullanici_id[0] = gizli_id
        aktif_kullanici_isim[0] = kadi
        sayfayi_kur()

    giris_butonu = ft.ElevatedButton("Cihazı Kaydet ve Gir", on_click=giris_yap_click, width=200)

    giris_ekrani = ft.Column([
        ft.Text("Planlayıcı", size=28, weight="bold"),
        kullanici_input,
        uyari_metni,
        giris_butonu
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    gorevler_kutusu = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    
    def tarih_secildi(e):
        if takvim and takvim.value:
            try:
                secilen_tarih = takvim.value.strftime("%Y-%m-%d")
            except:
                try:
                    secilen_tarih = datetime.strptime(str(takvim.value).split()[0], "%Y-%m-%d").strftime("%Y-%m-%d")
                except:
                    secilen_tarih = datetime.now(TR_TZ).strftime("%Y-%m-%d")
            gorev_tarihi_input.value = secilen_tarih
            gorevleri_yukle(secilen_tarih)
            page.update()

    takvim = None
    try:
        takvim = ft.DatePicker(
            first_date=datetime(2023, 1, 1),
            last_date=datetime(2035, 12, 31),
            on_change=tarih_secildi
        )
        page.overlay.append(takvim)
    except: pass

    gorev_tarihi_input = ft.TextField(
        value=datetime.now(TR_TZ).strftime("%Y-%m-%d"), 
        label="Tarih", width=120, text_align=ft.TextAlign.CENTER, read_only=True
    )
    
    def takvim_ac(e):
        if takvim:
            try:
                takvim.pick_date()
            except:
                try:
                    takvim.open = True
                    page.update()
                except: pass

    takvim_butonu = ft.TextButton(
        "📅", 
        tooltip="Takvimden Seç",
        on_click=takvim_ac,
        disabled=(takvim is None)
    )

    tarih_alani = ft.Row([gorev_tarihi_input, takvim_butonu], spacing=5)
    
    yeni_gorev_input = ft.TextField(hint_text="Görev yazın...", expand=True)
    
    renk_secimi = ft.Dropdown(
        options=[
            ft.dropdown.Option("blue", "Normal"),
            ft.dropdown.Option("red", "Acil"),
            ft.dropdown.Option("green", "Rahat")
        ],
        value="blue", width=100
    )

    def gorevi_guncelle(tarih, index, yeni_durum):
        data = veri_cek()
        k = aktif_kullanici_id[0]
        if k in data and tarih in data[k] and len(data[k][tarih]) > index:
            if isinstance(data[k][tarih][index], dict):
                data[k][tarih][index]["done"] = yeni_durum
                veri_kaydet(data)
        gorevleri_yukle(tarih)

    def gorevi_sil(e):
        try:
            tarih = e.control.data["tarih"]
            index = e.control.data["index"]
            data = veri_cek()
            k = aktif_kullanici_id[0]
            if k in data and tarih in data[k] and len(data[k][tarih]) > index:
                data[k][tarih].pop(index)
                veri_kaydet(data)
            gorevleri_yukle(tarih)
        except: pass

    def checkbox_degisti(e):
        try:
            tarih = e.control.data["tarih"]
            index = e.control.data["index"]
            yeni_durum = e.control.value
            gorevi_guncelle(tarih, index, yeni_durum)
        except: pass

    def gorevleri_yukle(secilen_tarih=None):
        gorevler_kutusu.controls.clear()
        if secilen_tarih is None:
            secilen_tarih = gorev_tarihi_input.value
        
        data = veri_cek()
        k = aktif_kullanici_id[0]
        user_data = data.get(k, {})
            
        if secilen_tarih in user_data and len(user_data[secilen_tarih]) > 0:
            for i, gorev in enumerate(user_data[secilen_tarih]):
                if isinstance(gorev, str):
                    metin = gorev
                    durum = False
                    renk = "blue"
                else:
                    metin = gorev.get("text", "")
                    durum = gorev.get("done", False)
                    renk = gorev.get("color", "blue")

                try: style = ft.TextStyle(color=renk, decoration=ft.TextDecoration.LINE_THROUGH if durum else ft.TextDecoration.NONE)
                except: style = None

                gorev_satiri = ft.Row(
                    controls=[
                        ft.Checkbox(
                            label=metin, 
                            value=durum, 
                            label_style=style,
                            data={"tarih": secilen_tarih, "index": i},
                            on_change=checkbox_degisti,
                            expand=True
                        ),
                        ft.TextButton(
                            "❌ Sil", 
                            data={"tarih": secilen_tarih, "index": i},
                            on_click=gorevi_sil
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
                gorevler_kutusu.controls.append(gorev_satiri)
        else:
            gorevler_kutusu.controls.append(ft.Text("Görev bulunmuyor.", italic=True, color="grey"))
        page.update()

    def gorev_ekle_click(e):
        if not yeni_gorev_input.value or not gorev_tarihi_input.value: return  
        hedef_tarih = gorev_tarihi_input.value
        ekle_butonu.disabled = True
        page.update()
        
        data = veri_cek()
        k = aktif_kullanici_id[0]
        
        if k not in data: data[k] = {}
        if hedef_tarih not in data[k]: data[k][hedef_tarih] = []
            
        yeni_gorev_objesi = {"text": yeni_gorev_input.value, "done": False, "color": renk_secimi.value}
        data[k][hedef_tarih].append(yeni_gorev_objesi)
        veri_kaydet(data)
            
        yeni_gorev_input.value = "" 
        ekle_butonu.disabled = False
        gorevleri_yukle(hedef_tarih)         

    ekle_butonu = ft.ElevatedButton("➕ Ekle", on_click=gorev_ekle_click)

    ust_satir = ft.Row(
        controls=[tarih_alani, renk_secimi],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    alt_satir = ft.Row(
        controls=[yeni_gorev_input, ekle_butonu],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    ekleme_satiri = ft.Column(
        controls=[ust_satir, alt_satir],
        spacing=10
    )

    def cikis_yap(e):
        try:
            if hasattr(page, "client_storage"):
                page.client_storage.remove("gizli_id")
                page.client_storage.remove("gorunen_isim")
        except: pass
        aktif_kullanici_id[0] = ""
        aktif_kullanici_isim[0] = ""
        page.controls.clear()
        page.add(ft.Row([giris_ekrani], alignment=ft.MainAxisAlignment.CENTER))
        page.update()

    def sayfayi_kur():
        page.controls.clear()
        page.appbar = ft.AppBar(
            title=ft.Text(f"Ajanda ({aktif_kullanici_isim[0]})"),
            bgcolor="blue900",
            actions=[
                ft.TextButton("🌙", on_click=tema_degistir, tooltip="Tema Değiştir"),
                ft.TextButton("🚪", on_click=cikis_yap, tooltip="Cihazdan Çıkış Yap")
            ]
        )
        page.add(
            gorevler_kutusu, 
            ft.Divider(), 
            ekleme_satiri
        )
        gorevleri_yukle()

    gizli_id = None
    gorunen_isim = None
    try:
        if hasattr(page, "client_storage"):
            gizli_id = page.client_storage.get("gizli_id")
            gorunen_isim = page.client_storage.get("gorunen_isim")
    except: pass

    if gizli_id:
        aktif_kullanici_id[0] = gizli_id
        aktif_kullanici_isim[0] = gorunen_isim if gorunen_isim else "Kullanıcı"
        sayfayi_kur()
        return

    page.add(ft.Row([giris_ekrani], alignment=ft.MainAxisAlignment.CENTER))

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
        
