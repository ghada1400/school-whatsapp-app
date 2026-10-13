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

st.set_page_config(page_title="نظام مراسلة المدارس - أ. غادة المجيبل", layout="wide")

st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-right: 5px solid #1E3A8A; text-align: right;'>
        <h2 style='margin: 0; color: #1E3A8A;'>🏫 نظام إدارة ومراسلة الطالبات الإلكتروني السحابي</h2>
        <p style='margin: 5px 0 0 0; color: #555;'>نظام المراسلة الفورية المطور والموثق لشبكة الإنترنت والجوالات</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 اختر ملف إكسل الطالبات (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    name_col, phone_col, class_col = None, None, None
    for col in df.columns:
        col_lower = col.lower()
        if "اسم" in col_lower or "name" in col_lower: name_col = col
        elif any(k in col_lower for k in ["جوال", "هاتف", "رقم", "phone", "mobile"]): phone_col = col
        elif any(k in col_lower for k in ["صف", "فصل", "class", "المرحلة"]): class_col = col

    if not name_col: name_col = df.columns
    if not phone_col: phone_col = df.columns if len(df.columns) > 1 else df.columns

    now = datetime.now()
    current_day_ar = DAYS_ARABIC.get(now.strftime("%A"), now.strftime("%A"))
    hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_date_str = f"{hijri_date.day} {HIJRI_MONTHS.get(hijri_date.month, '')} {hijri_date.year} هـ"

    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown("### 📌 خيارات التصفية")
        filtered_df = df.copy()
        if class_col:
            df[class_col] = df[class_col].astype(str).str.strip()
            unique_classes = df[class_col].dropna().unique()
            selected_class = st.selectbox("اختر الصف الدراسي:", ["عرض جميع الصفوف"] + list(unique_classes))
            if selected_class != "عرض جميع الصفوف":
                filtered_df = df[df[class_col] == selected_class].copy()

    with col_right:
        st.markdown("### 📝 نص الرسالة الموحدة")
        st.caption(f"💡 الاختصارات: [اسم الطالبة] | [اليوم] ({current_day_ar}) | [التاريخ الهجري] ({hijri_date_str})")
        default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
        message_text = st.text_area("تعديل نص الرسالة:", value=default_text, height=100)

    if "Select" not in filtered_df.columns:
        filtered_df.insert(0, "Select", False)

    st.markdown("---")
    st.markdown("### 👥 حدد الطالبات المُراد مراسلتهن:")
    st.write(f"📊 عدد الطالبات المتاحات في هذا العرض: **{len(filtered_df)} طالبة**")

    edited_df = st.data_editor(
        filtered_df,
        column_config={"Select": st.column_config.CheckboxColumn("اختيار (✓)", default=False)},
        disabled=[c for c in filtered_df.columns if c != "Select"],
        hide_index=True,
        use_container_width=True,
        key="cloud_perfect_selection_grid_fixed_final_v5"
    )
    
    selected_students = edited_df[edited_df["Select"] == True]
    
    st.markdown("---")
    st.markdown(f"### 🚀 قائمة أزرار الإرسال الفوري المجهزة ({len(selected_students)} طالبة مختارة):")
    
    if len(selected_students) == 0:
        st.info("💡 الرجاء وضع علامة صح (✓) أمام أسماء الطالبات في الجدول بالأعلى ليتم إنشاء أزرار إرسال مخصصة لهن هنا فوراً.")
    else:
        for index, row in selected_students.iterrows():
            name = str(row[name_col])
            phone = str(row[phone_col]).strip()
            
            phone = "".join(filter(str.isdigit, phone))
            if phone.startswith("05") and len(phone) == 10: phone = "966" + phone[1:]
            elif phone.startswith("5") and len(phone) == 9: phone = "966" + phone
                
            custom_message = message_text.replace("[اسم الطالبة]", name)
            custom_message = custom_message.replace("[اليوم]", current_day_ar)
            custom_message = custom_message.replace("[التاريخ الهجري]", hijri_date_str)
            
            encoded_message = urllib.parse.quote(custom_message)
            whatsapp_url = f"https://wa.me{phone}?text={encoded_message}"
            
            st.link_button(f"💬 اضغط لإرسال رسالة الطالبة: {name}", whatsapp_url, use_container_width=True)

st.markdown("""
    <hr style='border-top: 1px solid #bbb;'>
    <div style='display: flex; justify-content: space-between; color: #888; font-size: 14px; direction: rtl;'>
        <div style='font-weight: bold; color: #1E3A8A;'>✨ تصميم واعداد : غادة المجيبل</div>
        <div>لوحة تحكم سحابية v5.2</div>
    </div>
""", unsafe_allow_html=True)
