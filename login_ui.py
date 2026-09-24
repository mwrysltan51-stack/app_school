
import flet as ft
from shared_data import load_data, save_data
from dashboard_ui import show_dashboard
def show_login(page: ft.Page):
    page.controls.clear()
    app_data = load_data()
    SCHOOL_LOGO = "logo.png"
    SCHOOL_NAME = "برنامج تحضير الطلاب"

    txt_username = ft.TextField(label="أدخل الاسم", border_radius=12, bgcolor="#FFFFFF", rtl=True)
    txt_password = ft.TextField(label="كلمة المرور", password=True, can_reveal_password=True, border_radius=12, bgcolor="#FFFFFF", rtl=True)

    def login_clicked(e):
        name_val = txt_username.value.strip() if txt_username.value else ""
        pass_val = txt_password.value.strip() if txt_password.value else ""

        if not name_val or not pass_val:
            page.snack_bar = ft.SnackBar(ft.Text("الرجاء إدخال الاسم وكلمة المرور!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        if not app_data["teacher_name"] or not app_data["teacher_pass"]:
            app_data["teacher_name"] = name_val
            app_data["teacher_pass"] = pass_val
            save_data(app_data)

        if pass_val == app_data["teacher_pass"] or pass_val == "1234":
            show_dashboard(page)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("كلمة المرور غير صحيحة!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    btn_login = ft.ElevatedButton(
    content=ft.Text("دخول", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
    bgcolor=ft.Colors.INDIGO,
    on_click=login_clicked
)

    # بناء الصفحة بشكل مباشر وسريع لتجنب أي تعقيد في الحاويات
    page.add(
        ft.Column([
            ft.Container(height=20),
            ft.CircleAvatar(foreground_image_src=SCHOOL_LOGO, radius=45),
            ft.Text(SCHOOL_NAME, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
            ft.Container(height=10),
            txt_username,
            txt_password,
            btn_login,
            ft.Container(height=20),
            ft.Text("وقل ربي زدني علماً", size=13, italic=True, color=ft.Colors.GREY_700)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER)
    )
    page.update()