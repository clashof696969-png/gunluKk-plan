import flet as ft
from datetime import datetime, timedelta, timezone
import requests

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
    
    aktif_kullanici = [""]

    # --- HATA ÖNLEYİCİ ZIRHLI HAFIZA FONKSİYONLARI ---
    def hafizaya_yaz(anahtar, deger):
        try:
            if hasattr(page, "client_storage"):
                page.client_storage.set(anahtar, deger)
            elif hasattr(page, "session"):
                page.session.set(anahtar, deger)
        except: pass

    def hafizadan_oku(anahtar):
        try:
            if hasattr(page, "client_storage"):
                return page.client_storage.get(anahtar)
            elif hasattr(page, "session"):
                return page.session.get(anahtar)
        except: pass
        return None

    def hafizadan_sil(anahtar):
        try:
            if hasattr(page, "client_storage"):
                page.client_storage.remove(anahtar)
            elif hasattr(page, "session"):
                page.session.remove(anahtar)
        except: pass

    def tema_degistir(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.update()
        if aktif_kullanici[0]:
            gorevleri_yukle()

    kullanici_input = ft.TextField(label="Kullanıcı Adı", width=250, text_align=ft.TextAlign.CENTER)
    sifre_input = ft.TextField(label="Şifre", width=250, text_align=ft.TextAlign.CENTER, password=True, can_reveal_password=True)
    beni_hatirla = ft.Checkbox(label="Beni Hatırla", value=True)
    uyari_metni = ft.Text("", color="red", size=14, weight="bold")

    def giris_basarili(kadi, sifre):
        aktif_kullanici[0] = kadi
        if beni_hatirla.value:
            hafizaya_yaz("kadi", kadi)
            hafizaya_yaz("sifre", sifre)
        else:
            hafizadan_sil("kadi")
            hafizadan_sil("sifre")
        sayfayi_kur()

    def giris_yap_click(e):
        kadi = kullanici_input.value.strip()
        sifre = sifre_input.value.strip()
        
        if not kadi or not sifre:
            uyari_metni.value = "Kullanıcı adı ve şifre boş bırakılamaz!"
            page.update()
            return

        data = veri_cek()
        sifreler = data.get("_passwords", {})

        if kadi in sifreler:
            if sifreler[kadi] == sifre:
                giris_basarili(kadi, sifre)
            else:
                uyari_metni.value = "Hatalı şifre girdiniz!"
                page.update()
        else:
            uyari_metni.value = "Kullanıcı bulunamadı. Lütfen Kayıt Olun."
            page.update()

    def kayit_ol_click(e):
        kadi = kullanici_input.value.strip()
        sifre = sifre_input.value.strip()

        if not kadi or not sifre:
            uyari_metni.value = "Kullanıcı adı ve şifre boş bırakılamaz!"
            page.update()
            return

        data = veri_cek()
        if "_passwords" not in data:
            data["_passwords"] = {}

        if kadi in data["_passwords"]:
            uyari_metni.value = "Bu kullanıcı adı zaten alınmış!"
            page.update()
        else:
            data["_passwords"][kadi] = sifre
            if kadi not in data:
                data[kadi] = {}
            veri_kaydet(data)
            giris_basarili(kadi, sifre)

    giris_butonlari = ft.Row([
        ft.ElevatedButton("Giriş Yap", on_click=giris_yap_click),
        ft.ElevatedButton("Kayıt Ol", on_click=kayit_ol_click)
    ], alignment=ft.MainAxisAlignment.CENTER)

    giris_ekrani = ft.Column([
        ft.Text("Giriş / Kayıt", size=30, weight="bold"),
        kullanici_input,
        sifre_input,
        beni_hatirla,
        uyari_metni,
        giris_butonlari
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    gorevler_kutusu = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    
    def tarih_secildi(e):
        if takvim and takvim.value:
            secilen_tarih = takvim.value.strftime("%Y-%m-%d")
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
        label="Tarih", width=120, text_align=ft.TextAlign.CENTER, read_only=(takvim is not None)
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
        k = aktif_kullanici[0]
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
            k = aktif_kullanici[0]
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
        k = aktif_kullanici[0]
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
        k = aktif_kullanici[0]
        
        if k not in data: data[k] = {}
        if hedef_tarih not in data[k]: data[k][hedef_tarih] = []
            
        yeni_gorev_objesi = {"text": yeni_gorev_input.value, "done": False, "color": renk_secimi.value}
        data[k][hedef_tarih].append(yeni_gorev_objesi)
        veri_kaydet(data)
            
        yeni_gorev_input.value = "" 
        ekle_butonu.disabled = False
        gorevleri_yukle(hedef_tarih)         

    ekle_butonu = ft.ElevatedButton("➕ Ekle", on_click=gorev_ekle_click)

    # --- MOBİL UYUMLU TASARIM: 2 SATIRA BÖLDÜK ---
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
        hafizadan_sil("kadi")
        hafizadan_sil("sifre")
        aktif_kullanici[0] = ""
        page.controls.clear()
        page.add(ft.Row([giris_ekrani], alignment=ft.MainAxisAlignment.CENTER))
        page.update()

    def sayfayi_kur():
        page.controls.clear()
        page.appbar = ft.AppBar(
            title=ft.Text(f"Ajanda ({aktif_kullanici[0]})"),
            bgcolor="blue900",
            actions=[
                ft.TextButton("🌙", on_click=tema_degistir, tooltip="Tema Değiştir"),
                ft.TextButton("🚪", on_click=cikis_yap, tooltip="Çıkış Yap")
            ]
        )
        page.add(
            gorevler_kutusu, 
            ft.Divider(), 
            ekleme_satiri
        )
        gorevleri_yukle()

    # --- UYGULAMA AÇILDIĞINDA OTOMATİK GİRİŞ KONTROLÜ ---
    kayitli_kadi = hafizadan_oku("kadi")
    kayitli_sifre = hafizadan_oku("sifre")
    
    if kayitli_kadi and kayitli_sifre:
        data = veri_cek()
        sifreler = data.get("_passwords", {})
        if kayitli_kadi in sifreler and sifreler[kayitli_kadi] == kayitli_sifre:
            aktif_kullanici[0] = kayitli_kadi
            sayfayi_kur()
            return

    page.add(ft.Row([giris_ekrani], alignment=ft.MainAxisAlignment.CENTER))

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
