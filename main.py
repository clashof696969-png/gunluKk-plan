import flet as ft
from datetime import datetime
import json

def main(page: ft.Page):
    page.title = "Günlük Planlayıcım"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    gorevler_kutu = ft.Column()
    yeni_gorev_input = ft.TextField(hint_text="Yeni bir görev yazın...", expand=True)

    def gorev_ekle_click(e):
        # Görev ekleme mantığın burada (eksiksiz olsun)
        pass 

    def gorevleri_yukle():
        gorevler_kutu.controls.clear()
        # JSON yükleme mantığın burada
        pass

    # BUTONUNUN YERİ TAM BURASI:
    ekle_butonu = ft.IconButton(
        icon="add",
        icon_color="blue",
        icon_size=40,
        on_click=gorev_ekle_click
    )

    ekleme_satiri = ft.Row(
        controls=[yeni_gorev_input, ekle_butonu],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.add(ekleme_satiri, gorevler_kutu)

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)
