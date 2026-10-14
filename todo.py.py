import streamlit as st
import pandas as pd
import urllib.parse
import re
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

st.set_page_config(page_title="نظام مراسلة المدارس السحابي - أ. غادة المجيبل", layout="wide")

# تصميم الهيدر العلوي المنسق والمحترف
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-right: 5px solid #1E3A8A; text-align: right;'>
        <h2 style='margin: 0; color: #1E3A8A;'>🏫 نظام إدارة ومراسلة الطالبات الإلكتروني السحابي المطور</h2>
        <p style='margin: 5px 0 0 0; color: #555;'>موقع ويب فوري وجاهز للاستخدام من أي كمبيوتر أو جوال داخل المدرسة بدون تثبيت برامج</p>
    </div>
""", unsafe_allow_html=True)

# 📂 1. رفع ملف الإكسل
uploaded_file = st.file_uploader("📂 اختر ملف إكسل الطالبات (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip() # تنظيف الأعمدة
    
    # تثبيت أسماء أعمدة ملف المدرسة الحقيقي بدقة
    name_col = "اسم الطالبة"
    phone_col = "رقم الهاتف"
    class_col = "الصف"

    if name_col in df.columns and phone_col in df.columns and class_col in df.columns:
        
        # حساب التاريخ الهجري الحالي وتثبيته
        now = datetime.now()
        current_day_ar = DAYS_ARABIC.get(now.strftime("%A"), now.strftime("%A"))
        hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
        hijri_date_str = f"{hijri_date.day} {HIJRI_MONTHS.get(hijri_date.month, '')} {hijri_date.year} هـ"

        # تصفية الفصول الدراسيّة
        st.markdown("### 📌 تصفية الفصول الدراسيّة")
        df[class_col] = df[class_col].astype(str).str.strip()
        unique_classes = df[class_col].dropna().unique()
        selected_class = st.selectbox("اختر الصف الدراسي:", ["عرض جميع الصفوف"] + list(unique_classes))
        
        filtered_df = df.copy()
        if selected_class != "عرض جميع الصفوف":
            filtered_df = df[df[class_col] == selected_class].copy()

        # نص الرسالة الموحدة
        st.markdown("---")
        st.markdown("### 📝 نص الرسالة الموحدة")
        st.caption(f"💡 الاختصارات: [اسم الطالبة] | [اليوم] ({current_day_ar}) | [التاريخ الهجري] ({hijri_date_str})")
        default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
        message_text = st.text_area("تعديل نص الرسالة:", value=default_text, height=100)

        st.markdown("---")
        st.markdown("### 👥 جدول الطالبات التنفيذي المباشر")
        st.write(f"📊 عدد الطالبات في العرض الحالي: **{len(filtered_df)} طالبة**")

        # 🔄 معالجة الأرقام وبناء الرابط بطريقة حتمية تمنع اختفاء الشرطة المائلة
        whatsapp_links = []
        for index, row in filtered_df.iterrows():
            name = str(row[name_col])
            phone_raw = str(row[phone_col]).strip()
            
            # استخراج الأرقام وتطهيرها من أي رموز مخفية
            phone_digits = re.sub(r'\D', '', phone_raw)
            
            # توحيد الرقم دولياً بالكامل
            if phone_digits.startswith("00966"):
                phone_final = phone_digits[5:]
            elif phone_digits.startswith("966"):
                phone_final = phone_digits[3:]
            elif phone_digits.startswith("05"):
                phone_final = phone_digits[1:]
            else:
                phone_final = phone_digits
                
            custom_message = message_text.replace("[اسم الطالبة]", name).replace("[اليوم]", current_day_ar).replace("[التاريخ الهجري]", hijri_date_str)
            encoded_message = urllib.parse.quote(custom_message)
            
            # 🚀 الحل البرمجي القاطع: استخدام دالة urljoin لإجبار دمج الشرطة المائلة ومنع المتصفح من حظرها أو ابتلاعها
            base_url = "https://wa.me"
            phone_and_text = f"966{phone_final}?text={encoded_message}"
            whatsapp_url = urllib.parse.urljoin(base_url, phone_and_text)
            whatsapp_links.append(whatsapp_url)
        
        display_df = filtered_df.copy()
        display_df["رابط المراسلة"] = whatsapp_links

        # عرض الجدول الاحترافي النهائي
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
            key="cloud_embedded_fixed_final_grid_v8_5"
        )
    else:
        st.error(f"❌ خطأ: تأكدي أن ملف الإكسل يحتوي بدقة على الأعمدة التالية بنفس المسمى: '{name_col}'، '{phone_col}'، '{class_col}'")

# --- الحقوق المنسقة أسفل الصفحة ---
st.markdown("""
    <hr style='border-top: 1px solid #bbb;'>
    <div style='display: flex; justify-content: space-between; color: #888; font-size: 14px; direction: rtl;'>
        <div style='font-weight: bold; color: #1E3A8A;'>✨ تصميم واعداد : غادة المجيبل</div>
        <div>لوحة تحكم سحابية v8.5 (نسخة الربط الحتمي)</div>
    </div>
""", unsafe_allow_html=True)
