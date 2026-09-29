import flet as ft
from login_ui import show_login
import traceback
def main(page: ft.Page):
    try:
        page.title = "برنامج تحضير الطلاب"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.bgcolor = "#F8F9FA"
        page.window_width = 460
        page.window_height = 850
        page.window_resizable = False
        show_login(page)
    except Exception as e:
        page.add(ft.Text(f"حدث خطأ برمجي: {e}\n{traceback.format_exc()}", color="red"))
        page.update()

ft.app(target=main)
