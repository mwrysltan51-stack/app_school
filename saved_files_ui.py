import flet as ft
import os
from shared_data import load_data
def show_saved_files(page: ft.Page, class_name: str, section_name: str):
    page.controls.clear()
    page.update()
    app_data = load_data()
    teacher_name = app_data.get("teacher_name", "غير محدد")
    subject_name = app_data.get("subject_name", "غير محدد")
    def go_back(e):
        from dashboard_ui import show_dashboard
        show_dashboard(page)

    header = ft.Column([
        ft.Row([
            ft.Text(f"الأستاذ / ة : {teacher_name}", size=15, weight="bold", color="black", rtl=True),
            ft.IconButton(icon=ft.Icons.ARROW_FORWARD, icon_color="black", on_click=go_back, tooltip="رجوع"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=True),
        ft.Text(f"المادة : {subject_name}", size=14, color="black", rtl=True),
        ft.Divider(color="black", height=2, thickness=1.5)
    ], rtl=True)

    section_data = app_data.get('classes_structure', {}).get(class_name, {}).get(section_name, {})
    saved_files = section_data.get("saved_files", [])

    content_column = ft.Column(spacing=20, expand=True)

    if not saved_files:
        content_column.controls.append(
            ft.Container(
                content=ft.Text("لا توجد ملفات تحضير محفوظة لهذه الشعبة حتى الآن.", color="red", size=16, weight="bold", text_align="center"),
                padding=20
            )
        )
    else:
        files_list_ui = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.END)

        # عرض الملفات المحفوظة فقط (بما أن النسخ وإنشاء المجلد تم تلقائياً عند ضغط زر الحفظ)
        for file_path in saved_files:
            file_name = os.path.basename(file_path)

            file_row = ft.Row([
                ft.Container(
                    content=ft.Text(file_name, color="black", size=13, weight="bold", text_align="right", rtl=True),
                    bgcolor="#D1D5DB", padding=10, border_radius=8, expand=True
                )
            ], alignment=ft.MainAxisAlignment.END, spacing=10, rtl=True)
            files_list_ui.controls.append(file_row)

        card_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(ft.Text(f"شعبة {section_name}", color="white", size=12, weight="bold"), bgcolor="#F97316", padding=5, border_radius=4),
                    ft.Container(ft.Text(f"الصف {class_name}", color="white", size=12, weight="bold"), bgcolor="#F97316", padding=5, border_radius=4)
                ], alignment=ft.MainAxisAlignment.END, spacing=5, rtl=True),
                ft.Divider(color="transparent", height=5),
                files_list_ui
            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=10),
            bgcolor="#EFF6FF", padding=15, border_radius=10
        )
        content_column.controls.append(card_content)

    page.add(
        ft.Container(
            content=ft.Column([header, ft.Divider(color="transparent", height=20), content_column]),
            padding=20, expand=True, bgcolor="white"
        )
    )