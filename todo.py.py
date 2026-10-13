import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from hijri_converter import Gregorian

# إعداد وتغيير أسماء الأيام والشهور الهجرية للعربية
DAYS_ARABIC = {
    "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
    "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
}

HIJRI_MONTHS = {
    1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الثاني",
    5: "جمادى الأولى", 6: "جمادى الآخرة", 7: "رجب", 8: "شعبان",
    9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة"
}

# إعدادات الصفحة وجعلها عريضة واحترافية
st.set_page_config(page_title="نظام مراسلة المدارس - أ. غادة المجيبل", layout="wide")

# تصميم الهيدر العلوي بشكل منسق
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-right: 5px solid #4CAF50;'>
        <h2 style='margin: 0; color: #1E3A8A;'>🏫 نظام إدارة ومراسلة الطالبات الإلكتروني</h2>
        <p style='margin: 5px 0 0 0; color: #555;'>نظام ذكي لفلترة الصفوف المدرسية والمراسلة الفورية المخصصة عبر الواتساب</p>
    </div>
""", unsafe_allow_html=True)

# 📂 1. رفع ملف الإكسل
uploaded_file = st.file_uploader("📂 اختر ملف إكسل الطالبات (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip() # تنظيف الأعمدة من المسافات
    
    # ⚙️ محاولة التعرف التلقائي الذكي على الأعمدة
    name_col, phone_col, class_col = None, None, None
    for col in df.columns:
        col_lower = col.lower()
        if "اسم" in col_lower or "name" in col_lower: name_col = col
        elif any(k in col_lower for k in ["جوال", "هاتف", "رقم", "phone", "mobile"]): phone_col = col
        elif any(k in col_lower for k in ["صف", "فصل", "class", "المرحلة"]): class_col = col

    if not name_col: name_col = df.columns[0]
    if not phone_col: phone_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    # حساب التاريخ الهجري الحالي وتثبيته
    now = datetime.now()
    current_day_ar = DAYS_ARABIC.get(now.strftime("%A"), now.strftime("%A"))
    hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_date_str = f"{hijri_date.day} {HIJRI_MONTHS.get(hijri_date.month, '')} {hijri_date.year} هـ"

    # تقسيم الشاشة العلوية إلى قسمين متناسقين (الفلتر + نص الرسالة)
    col_left, col_right = st.columns([1, 2], gap="large")
    
    with col_left:
        st.markdown("### 📌 خيارات التصفية")
        filtered_df = df.copy()
        if class_col:
            df[class_col] = df[class_col].astype(str).str.strip()
            unique_classes = df[class_col].dropna().unique()
            selected_class = st.selectbox("اختر الصف الدراسي:", ["عرض جميع الصفوف"] + list(unique_classes))
            if selected_class != "عرض government الصفوف" and selected_class != "عرض جميع الصفوف":
                filtered_df = df[df[class_col] == selected_class].copy()
        else:
            st.info("لم يتم العثور على عمود خاص بالصفوف في الملف.")

    with col_right:
        st.markdown("### 📝 نص الرسالة الموحدة")
        st.caption(f"💡 الاختصارات النشطة: [اسم الطالبة] | [اليوم] ({current_day_ar}) | [التاريخ الهجري] ({hijri_date_str})")
        default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
        message_text = st.text_area("تعديل نص الرسالة:", value=default_text, height=100)

    st.markdown("---")
    st.markdown("### 👥 جدول الطالبات التنفيذي المطور")
    st.write(f"📊 عدد الطالبات في العرض الحالي: **{len(filtered_df)} طالبة**")

    # 🔄 تجهيز الروابط وتضمينها كعمود تفاعلي احترافي داخل الجدول
    links = []
    for index, row in filtered_df.iterrows():
        name = str(row[name_col])
        phone = str(row[phone_col]).strip()
        
        # معالجة أرقام الهواتف دولياً
        phone = "".join(filter(str.isdigit, phone))
        if phone.startswith("05") and len(phone) == 10: phone = "966" + phone[1:]
        elif phone.startswith("5") and len(phone) == 9: phone = "966" + phone
            
        custom_message = message_text.replace("[اسم الطالبة]", name)
        custom_message = custom_message.replace("[اليوم]", current_day_ar)
        custom_message = custom_message.replace("[التاريخ الهجري]", hijri_date_str)
        
        encoded_message = urllib.parse.quote(custom_message)
        whatsapp_url = f"https://whatsapp.com{phone}&text={encoded_message}"
        links.append(whatsapp_url)
    
    # إضافة عمود الرابط للجدول المعروض
    display_df = filtered_df.copy()
    display_df["رابط المراسلة"] = links

    # عرض الجدول الاحترافي النهائي مع تحويل عمود الروابط إلى أزرار ضغط ذكية وجذابة داخل السطر
    st.data_editor(
        display_df,
        column_config={
            "رابط المراسلة": st.column_config.LinkColumn(
                "💬 إرسال الواتساب",
                help="اضغط لفتح محادثة الطالبة فوراً بالرسالة المجهزة",
                display_text="💬 إرسال الآن"
            )
        },
        disabled=display_df.columns,
        hide_index=True,
        use_container_width=True,
        key="styled_students_grid"
    )

# --- التوقيع والحقوق المنسقة أسفل الصفحة ---
st.markdown("""
    <hr style='border-top: 1px solid #bbb;'>
    <div style='display: flex; justify-content: space-between; color: #888; font-size: 14px;'>
        <div>لوحة تحكم سحابية v2.0</div>
        <div style='font-weight: bold; color: #1E3A8A;'>✨ تصميم واعداد : غادة المجيبل</div>
    </div>
""", unsafe_allow_html=True)
