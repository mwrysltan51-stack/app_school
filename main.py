import flet as ft
from login_ui import show_login
def main(page: ft.Page):
    page.title = "برنامج تحضير الطلاب"
    page.icon="icon.png"
    page.window_icon="icon.png"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#F8F9FA"
    page.window_width = 460
    page.window_height = 850
    page.window_resizable = False
    # === السر الهندسي: زراعة أداة المشاركة في جذر التطبيق ===
    page.share_control = ft.Share()
    page.overlay.append(page.share_control)
    # ========================================================

    show_login(page)

ft.app(target=main, assets_dir="assets")