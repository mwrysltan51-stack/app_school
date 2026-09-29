import flet as ft
import traceback

def main(page: ft.Page):
    try:
        page.title = "برنامج تحضير الطلاب"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.bgcolor = "#F8F9FA"
        page.scroll = ft.ScrollMode.AUTO

        # === زراعة أداة المشاركة في جذر التطبيق ===
        page.share_control = ft.Share()
        page.overlay.append(page.share_control)
        # ==========================================

        # استدعاء واجهة تسجيل الدخول
        from login_ui import show_login
        show_login(page)

    except Exception as e:
        # إذا حدث أي خطأ برمجي أو في استدعاء الملفات، سيظهر لك هنا باللون الأحمر
        page.clean()
        page.add(
            ft.Text("حدث خطأ أثناء تشغيل التطبيق:", color="red", size=18, weight="bold", rtl=True),
            ft.Text(traceback.format_exc(), color="black", size=12, selectable=True, rtl=False)
        )
        page.update()

# إزالة assets_dir لتجنب أي انهيار بسبب نقص ملفات الصور
ft.app(target=main)
