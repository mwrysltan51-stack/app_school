import flet as ft
import openpyxl
import os
import shutil
from datetime import datetime, timedelta
from shared_data import load_data, save_data

def show_attendance(page: ft.Page, class_name: str, section_name: str):
    page.controls.clear()
    page.update()
    app_data = load_data()
    
    if class_name not in app_data['classes_structure']:
        app_data['classes_structure'][class_name] = {}
    if section_name not in app_data['classes_structure'][class_name]:
        app_data['classes_structure'][class_name][section_name] = {"students": [], "attendance_records": {}, "saved_files": []}

    section_data = app_data['classes_structure'][class_name][section_name]
    students_list = section_data.get("students", [])

    if not students_list:
        page.snack_bar = ft.SnackBar(ft.Text("لا يوجد طلاب مسجلين! يرجى رفع ملف الإكسل أولاً."), bgcolor="#EF4444")
        page.snack_bar.open = True
        from dashboard_ui import show_dashboard
        show_dashboard(page)
        return

    today_date = datetime.now().strftime("%Y-%m-%d")

    students_names = []
    for st in students_list:
        vals = list(st.values())
        if len(vals) > 1:
            students_names.append(str(vals[1]))
        elif len(vals) > 0:
            students_names.append(str(vals[0]))

    if "attendance_records" not in section_data:
        section_data["attendance_records"] = {}

    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cleaned_records = {}
    for d_key in [today_date, yesterday_date]:
        if d_key in section_data["attendance_records"]:
            cleaned_records[d_key] = section_data["attendance_records"][d_key]
    section_data["attendance_records"] = cleaned_records

    if today_date not in section_data["attendance_records"]:
        section_data["attendance_records"][today_date] = {}

    attendance_state = section_data["attendance_records"][today_date]

    def go_back(e):
        from dashboard_ui import show_dashboard
        show_dashboard(page)

    header = ft.Container(
        content=ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_FORWARD, icon_color="#1E3A8A", on_click=go_back, tooltip="رجوع"),
            ft.Text(f"الشعبة : {section_name}", size=16, weight="bold", color="#1E3A8A"),
            ft.Text(f"الصف : {class_name}", size=16, weight="bold", color="#1E3A8A"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=True),
        bgcolor="#E0F2FE", padding=10, border_radius=8
    )

    students_column = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, expand=True)

    def build_students_table(search_query=""):
        students_column.controls.clear()

        table_header = ft.Row([
            ft.Container(ft.Text("الحالة", weight="bold", color="white", text_align="center"), width=120, bgcolor="#374151", padding=5, border_radius=4),
            ft.Container(ft.Text("اسم الطالب", weight="bold", color="white", text_align="center"), expand=True, bgcolor="#374151", padding=5, border_radius=4),
            ft.Container(ft.Text("الرقم", weight="bold", color="white", text_align="center"), width=50, bgcolor="#374151", padding=5, border_radius=4),
        ], rtl=True, spacing=2)
        students_column.controls.append(table_header)

        for index, name in enumerate(students_names):
            if search_query in name:
                status = attendance_state.get(name, None)

                green_color = "#65A30D" if status == "حاضر" else "#E5E7EB"
                red_color = "#DC2626" if status == "غائب" else "#E5E7EB"
                row_bg = "#F3F4F6" if index % 2 == 0 else "#FFFFFF"

                btn_present = ft.Container(
                    content=ft.Row([ft.Text("حاضر", size=11, weight="bold", color="black" if status == "حاضر" else "#374151")], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=green_color, width=50, height=28, border_radius=4,
                    on_click=lambda e, n=name: set_status(n, "حاضر")
                )

                btn_absent = ft.Container(
                    content=ft.Row([ft.Text("غائب", size=11, weight="bold", color="black" if status == "غائب" else "#374151")], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=red_color, width=50, height=28, border_radius=4,
                    on_click=lambda e, n=name: set_status(n, "غائب")
                )

                row = ft.Container(
                    content=ft.Row([
                        ft.Container(ft.Row([btn_present, btn_absent], spacing=5, alignment=ft.MainAxisAlignment.CENTER), width=120, padding=5),
                        ft.Container(ft.Text(name, color="black", size=13, text_align="center"), expand=True, padding=5),
                        ft.Container(ft.Text(str(index + 1), color="black", text_align="center"), width=50, padding=5),
                    ], rtl=True, spacing=2),
                    bgcolor=row_bg, border_radius=4
                )
                students_column.controls.append(row)
        page.update()

    def set_status(student_name, status):
        attendance_state[student_name] = status
        build_students_table(search_input.value)

    search_input = ft.TextField(
        hint_text="بحث عن اسم",
        text_align=ft.TextAlign.CENTER,
        bgcolor="#F59E0B", color="white",
        hint_style=ft.TextStyle(color="white", weight="bold"),
        border_radius=8, content_padding=5,
        on_change=lambda e: build_students_table(e.control.value)
    )

    def delete_selections(e):
        attendance_state.clear()
        search_input.value = ""
        build_students_table()
        page.snack_bar = ft.SnackBar(ft.Text("تم مسح التحديدات لهذا اليوم!"), bgcolor="#EF4444")
        page.snack_bar.open = True
        page.update()

    def save_and_export(e):
        # تعريف الزر أولاً بشكل آمن لتجنب أي خطأ
        nonlocal btn_save

        section_data["attendance_records"][today_date] = attendance_state

        excel_data = []
        for i, name in enumerate(students_names):
            stat = attendance_state.get(name, "فارغ / عذر")
            excel_data.append({
                "رقم_الطالب": i + 1,
                "اسم_الطالب": name,
                "الحالة": stat
            })

        file_name = f"تحضير_{class_name}_شعبة_{section_name}_{today_date}.xlsx"

        try:
            # مسار التخزين (ويندوز أو أندرويد)
            android_downloads = "/storage/emulated/0/Download"
            if os.path.exists(android_downloads):
                safe_base = android_downloads
            else:
                safe_base = os.path.join(os.path.expanduser("~"), "Documents")

            # إنشاء شجرة المجلدات: تحضير الطلاب -> الصف -> الشعبة
            main_parent_folder = os.path.join(safe_base, "تحضير الطلاب")
            if not os.path.exists(main_parent_folder):
                os.makedirs(main_parent_folder, exist_ok=True)

            class_folder = os.path.join(main_parent_folder, class_name)
            if not os.path.exists(class_folder):
                os.makedirs(class_folder, exist_ok=True)

            section_folder = os.path.join(class_folder, f"شعبة {section_name}")
            if not os.path.exists(section_folder):
                os.makedirs(section_folder, exist_ok=True)

            final_file_path = os.path.join(section_folder, file_name)

            # حفظ ملف الإكسل الأساسي
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            ws.append(["رقم_الطالب", "اسم_الطالب", "الحالة"])
            for item in excel_data:
                ws.append([item["رقم_الطالب"], item["اسم_الطالب"], item["الحالة"]])
            wb.save(final_file_path)
            
            # -------------------------------------------------------------
            # --- التعديل الجديد: إنشاء مجلد "تحضير اليوم" وتحديث محتواه ---
            # -------------------------------------------------------------
            today_folder = os.path.join(main_parent_folder, "تحضير اليوم")
            if not os.path.exists(today_folder):
                os.makedirs(today_folder, exist_ok=True)
                
            # تنظيف ملفات الأيام السابقة من مجلد تحضير اليوم
            for file_in_dir in os.listdir(today_folder):
                if today_date not in file_in_dir:
                    old_file_path = os.path.join(today_folder, file_in_dir)
                    try:
                        if os.path.isfile(old_file_path):
                            os.remove(old_file_path)
                    except Exception as ex:
                        print(f"Error removing old file: {ex}")
                        
            # نسخ ملف الإكسل الحالي إلى مجلد تحضير اليوم
            today_file_path = os.path.join(today_folder, file_name)
            shutil.copy(final_file_path, today_file_path)
            # -------------------------------------------------------------

            # إدارة السجلات للحفاظ على آخر ملفين في مجلد الشعبة
            if "saved_files" not in section_data:
                section_data["saved_files"] = []

            saved_list = section_data["saved_files"]
            if final_file_path not in saved_list:
                saved_list.append(final_file_path)

            if len(saved_list) > 2:
                oldest_file = saved_list.pop(0)
                if os.path.exists(oldest_file):
                    try:
                        os.remove(oldest_file)
                    except:
                        pass
            section_data["saved_files"] = saved_list

        except Exception as ex:
            print(f"Error saving: {ex}")

        save_data(app_data)

        # تحديث شكل الزر بأمان تام
        btn_save.bgcolor = "#1E3A8A"
        btn_save.text = "تم الحفظ ✓"

        page.snack_bar = ft.SnackBar(
            ft.Text(f"تم الحفظ بنجاح وتحديث مجلد 'تحضير اليوم'", rtl=True),
            bgcolor="#10B981"
        )
        page.snack_bar.open = True
        page.update()

    btn_save = ft.ElevatedButton("حفظ", on_click=save_and_export, bgcolor="#3B82F6", color="white", width=100)
    btn_delete = ft.ElevatedButton("مسح التحديدات", on_click=delete_selections, bgcolor="#EF4444", color="white", width=120)

    footer_buttons = ft.Row([btn_save, btn_delete], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
    date_text = ft.Text(f"التاريخ : {today_date}", size=14, weight="bold", color="black", rtl=True)

    build_students_table()

    page.add(
        ft.Container(
            content=ft.Column([
                header,
                search_input,
                students_column,
                ft.Divider(color="transparent", height=10),
                footer_buttons,
                ft.Container(content=date_text, padding=10)
            ], expand=True),
            bgcolor="white", padding=10, expand=True
        )
    )

