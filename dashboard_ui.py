import flet as ft
import openpyxl
import os
from attendance_ui import show_attendance
from saved_files_ui import show_saved_files
from shared_data import load_data, save_data
def show_dashboard(page: ft.Page):
    page.controls.clear()
    page.overlay.clear() # تنظيف التراكب لتجنب تضارب العناصر
    page.update()
    app_data = load_data()

    # ==========================================
    # إعداد أداة اختيار الملفات (FilePicker)
    # ==========================================
    current_pick = {"class_name": None, "section_name": None}

    def on_file_picked(e):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            c_name = current_pick["class_name"]
            s_name = current_pick["section_name"]

            if c_name and s_name:
                try:
                                 # قراءة الإكسل بدون بانداس
                        wb = openpyxl.load_workbook(file_path, data_only=True)
                        sheet = wb.active
                        students_list = []

                        rows = list(sheet.iter_rows(values_only=True))
                        if len(rows) > 1:
                            headers = [str(h) if h is not None else f"Column{i}" for i, h in enumerate(rows[0])]
                            for row in rows[1:]:
                                # التحقق من أن الصف ليس فارغاً تماماً
                                if any(row):
                                    student_dict = {headers[i]: (row[i] if row[i] is not None else "") for i in range(len(headers))}
                                    students_list.append(student_dict)
                        app_data['classes_structure'][c_name][s_name]["file_path"] = file_path
                        app_data['classes_structure'][c_name][s_name]["students"] = students_list

                        save_data(app_data)
                        rebuild_class_cards()

                        page.snack_bar = ft.SnackBar(ft.Text(f"تم رفع الملف لشعبة {s_name} بنجاح!"), bgcolor="#10B981")
                        page.snack_bar.open = True
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(ft.Text("عذراً، حدث خطأ في قراءة ملف الإكسل!"), bgcolor="#EF4444")
                    page.snack_bar.open = True
                page.update()

    # إنشاء الأداة وربطها بالدالة بالطريقة الآمنة
    file_picker = ft.FilePicker()
    file_picker.on_result = on_file_picked
    page.overlay.append(file_picker)
    page.update() # خطوة حاسمة جداً لتعريف الأداة في النظام قبل استخدامها

    def initiate_file_pick(class_name, section_name):
        current_pick["class_name"] = class_name
        current_pick["section_name"] = section_name
        file_picker.pick_files(allowed_extensions=["xlsx", "xls"])

    # ==========================================
    # إعدادات النصوص العلوية
    # ==========================================
    teacher_text = ft.Text(f"الأستاذ/ة :{app_data['teacher_name']}", size=16, weight=ft.FontWeight.BOLD, color="#1E293B", rtl=True)
    subject_text = ft.Text(f"المادة: {app_data['subject_name']}", size=14, color="#475569", rtl=True)

    # ==========================================
    # نافذة الإعدادات
    # ==========================================
    input_name = ft.TextField(label="اسم الأستاذ", value=app_data['teacher_name'], rtl=True)
    input_pass = ft.TextField(label="كلمة المرور", value=app_data['teacher_pass'], password=True, can_reveal_password=True, rtl=True)
    input_subject = ft.TextField(label="اسم المادة", value=app_data['subject_name'], rtl=True)
    input_class_name = ft.TextField(label="اسم الصف (مثال: الصف الثالث الثانوي)", rtl=True)
    input_sections = ft.TextField(label="الشعب مفصولة بفاصلة مثل: أ، ب، ج", rtl=True)

    temp_classes_preview = ft.Column([], rtl=True)
    temp_classes_structure = {}

    def update_temp_preview():
        temp_classes_preview.controls.clear()
        for c_name, secs in list(temp_classes_structure.items()):
            secs_str = " ، ".join(secs.keys())
            def delete_class(e, name=c_name):
                if name in temp_classes_structure:
                    del temp_classes_structure[name]
                    update_temp_preview()

            temp_classes_preview.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"• {c_name} (الشعب: {secs_str})", size=12, color="#334155", rtl=True, expand=True),
                        ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red400", icon_size=18, tooltip="حذف هذا الصف", on_click=delete_class)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=True),
                    padding=5, bgcolor="#F1F5F9", border_radius=6
                )
            )
        page.update()

    def add_temp_class(e):
        c_name = input_class_name.value.strip()
        s_raw = input_sections.value.strip()
        if c_name and s_raw:
            sections_list = [s.strip() for s in s_raw.split(",") if s.strip()]
            if c_name not in temp_classes_structure:
                temp_classes_structure[c_name]={}
            
            for sec in sections_list:
                if sec not in temp_classes_structure[c_name]:
                    temp_classes_structure[c_name][sec]={"file_path": None,"students":[]}
            input_class_name.value = ""
            input_sections.value = ""
            update_temp_preview()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("الرجاء إدخال اسم الصف والشعب!"), bgcolor="#EF4444")
            page.snack_bar.open = True
            page.update()

    # ==========================================
    # بناء الكروت (الصفوف) في الواجهة الرئيسية
    # ==========================================
    classes_container_column = ft.Column([], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

    def rebuild_class_cards():
        classes_container_column.controls.clear()
        for class_name, sections_dict in app_data['classes_structure'].items():
            section_controls = []
            for sec_name, sec_data in sections_dict.items():
                has_file = sec_data["file_path"] is not None
                upload_btn_color = "#10B981" if has_file else "#4F46E5"
                upload_btn_text = "تغيير الملف" if has_file else "رفع الملف"

                section_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Row([
                                ft.Container(content=ft.Text(f"شعبة {sec_name}", color="#FFFFFF", weight=ft.FontWeight.BOLD, size=12, rtl=True), bgcolor="#F97316", padding=7, border_radius=6),
                                ft.Text("مرفق ✓" if has_file else "غير مرفق", size=11, color="#10B981" if has_file else "#94A3B8", weight=ft.FontWeight.BOLD, rtl=True),
                            ], spacing=10, rtl=True),

                            ft.Row([
                            ft.ElevatedButton(content=ft.Text(upload_btn_text, color="#FFFFFF", size=10, rtl=True), bgcolor=upload_btn_color, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=5), on_click=lambda e, c=class_name, s=sec_name: initiate_file_pick(c, s)),
                            ft.ElevatedButton(content=ft.Text("الملفات المحفوظة", color="#FFFFFF", size=10, rtl=True), bgcolor="#3B82F6", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=5), on_click=lambda e, c=class_name, s=sec_name: show_saved_files(page, c, s)),
                            ft.ElevatedButton(content=ft.Text("تحضير", color="#FFFFFF", size=10, rtl=True), bgcolor="#059669", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=5), on_click=lambda e, c=class_name, s=sec_name: show_attendance(page, c, s))
                        ], spacing=6, rtl=True)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=True),
                        padding=8, bgcolor="#F8FAFC", border_radius=8,
                    )
                )

            class_card = ft.Container(
                content=ft.Column([
                    ft.Text(f"الصف : {class_name}", size=14, weight=ft.FontWeight.BOLD, color="#1E293B", rtl=True),
                    ft.Divider(color="#E2E8F0", height=6),
                    ft.Column(section_controls, spacing=6)
                ], rtl=True),
                bgcolor="#FFFFFF", padding=12, border_radius=12, width=440,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color="#0000000A"), margin=6,
            )
            classes_container_column.controls.append(class_card)
        page.update()

    def save_all_settings(e):
        app_data['teacher_name'] = input_name.value
        app_data['teacher_pass'] = input_pass.value
        app_data['subject_name'] = input_subject.value
        app_data['classes_structure'] = temp_classes_structure.copy()

        save_data(app_data)

        teacher_text.value = f"الأستاذ / {app_data['teacher_name']}"
        subject_text.value = f"المادة: {app_data['subject_name']}"
        rebuild_class_cards()

        settings_dialog.open = False
        page.snack_bar = ft.SnackBar(ft.Text("تم حفظ الإعدادات بنجاح!"), bgcolor="#10B981")
        page.snack_bar.open = True
        page.update()

    settings_dialog = ft.AlertDialog(
        title=ft.Text("لوحة الإعدادات وإدارة الصفوف", rtl=True, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                ft.Text("بيانات الأستاذ والمادة", weight=ft.FontWeight.BOLD, size=13, color="#4F46E5", rtl=True),
                input_name, input_pass, input_subject,
                ft.Divider(height=15),
                ft.Text("إضافة الصفوف والشعب", weight=ft.FontWeight.BOLD, size=13, color="#4F46E5", rtl=True),
                input_class_name, input_sections,
                ft.ElevatedButton(content=ft.Text("إضافة صف إلى القائمة +", color="#FFFFFF", size=12), bgcolor="#4F46E5", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)), on_click=add_temp_class),
                ft.Text("الصفوف المضافة حالياً:", size=11, weight=ft.FontWeight.BOLD, color="#64748B", rtl=True),
                temp_classes_preview,
            ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO, rtl=True),
            width=380, height=450,
        ),
        actions=[
            ft.ElevatedButton(content=ft.Text("حفظ الكل", color="#FFFFFF"), bgcolor="#10B981", on_click=save_all_settings),
            ft.TextButton("إلغاء", on_click=lambda e: setattr(settings_dialog, 'open', False) or page.update()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(settings_dialog)

    def open_settings(e):
        temp_classes_structure.clear()
        for c, s in app_data['classes_structure'].items():
            temp_classes_structure[c] = s.copy()
        update_temp_preview()
        settings_dialog.open = True
        page.update()

    header_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(content=ft.Text("الإعدادات ⚙", color="#4F46E5", weight=ft.FontWeight.BOLD, size=13), bgcolor="#EEF2FF", padding=10, border_radius=8, on_click=open_settings),
                teacher_text,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color="#CBD5E1", height=15),
            subject_text,
        ]),
        bgcolor="#FFFFFF", padding=20, border_radius=15, width=420, shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color="#0000000A"), margin=10,
    )

    rebuild_class_cards()
    page.add(
        ft.Column([
            header_card,
            ft.Text("إدارة الشعب وكشوفات الطلاب", size=14, weight=ft.FontWeight.BOLD, color="#334155", rtl=True),
            classes_container_column,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO ,expand=True)
    )