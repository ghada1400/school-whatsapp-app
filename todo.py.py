import streamlit as st
import pandas as pd
import time
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

st.set_page_config(page_title="نظام مراسلة المدارس الجماعي - أ. غادة المجيبل", layout="wide")

# تصميم الهيدر العلوي المنسق والمحترف
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-right: 5px solid #1E3A8A; text-align: right;'>
        <h2 style='margin: 0; color: #1E3A8A;'>🏫 نظام إدارة ومراسلة الطالبات الإلكتروني التلقائي المحلي</h2>
        <p style='margin: 5px 0 0 0; color: #555;'>نظام ذكي مطابق لملف المدرسة للمراسلة الجماعية التلقائية دفعة واحدة بدون تدخل</p>
    </div>
""", unsafe_allow_html=True)

# 📂 1. رفع ملف الإكسل
uploaded_file = st.file_uploader("📂 اختر ملف إكسل الطالبات (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip() # تنظيف أسماء الأعمدة من أي مسافات زائدة
    
    # ⚙️ التثبيت الصريح والمطابق لأسماء أعمدة ملفك الحقيقي
    name_col = "اسم الطالبة"
    phone_col = "رقم الهاتف"
    class_col = "الصف"

    # التحقق من وجود الأعمدة في الملف المرفوع لمنع الأخطاء
    if name_col in df.columns and phone_col in df.columns and class_col in df.columns:
        st.success("تم تحميل بيانات ملف المدرسة والتعرف على الفصول بنجاح!")
        
        # حساب التاريخ الهجري الحالي وتثبيته
        now = datetime.now()
        current_day_ar = DAYS_ARABIC.get(now.strftime("%A"), now.strftime("%A"))
        hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
        hijri_date_str = f"{hijri_date.day} {HIJRI_MONTHS.get(hijri_date.month, '')} {hijri_date.year} هـ"

        # تصفية الفصول والصفوف بدقة
        st.markdown("### 📌 تصفية الفصول الدراسيّة")
        df[class_col] = df[class_col].astype(str).str.strip()
        unique_classes = df[class_col].dropna().unique()
        
        # عرض جميع الصفوف المكتوبة في ملفك (أول، ثاني، ثالث، رابع...)
        selected_class = st.selectbox("اختر الصف لعرض طالباته فقط:", ["عرض جميع الصفوف"] + list(unique_classes))
        
        filtered_df = df.copy()
        if selected_class != "عرض جميع الصفوف":
            filtered_df = df[df[class_col] == selected_class].copy()

        # كود نص الرسالة الموحدة المطور
        st.markdown("---")
        st.markdown("### 📝 نص الرسالة الموحدة")
        st.caption(f"💡 الاختصارات النشطة: [اسم الطالبة] | [اليوم] ({current_day_ar}) | [التاريخ الهجري] ({hijri_date_str})")
        default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
        message_text = st.text_area("تعديل نص الرسالة:", value=default_text, height=100)

        # إضافة عمود الاختيار التفاعلي (✓) للجدول بصرياً
        if "Select" not in filtered_df.columns:
            filtered_df.insert(0, "Select", False)

        st.markdown("---")
        st.markdown("### 👥 حدد الطالبات المُراد مراسلتهن تلقائياً:")
        st.write(f"📊 عدد الطالبات المتاحات في هذا الصف: **{len(filtered_df)} طالبة**")

        # عرض الجدول الاحترافي الجميل
        edited_df = st.data_editor(
            filtered_df,
            column_config={"Select": st.column_config.CheckboxColumn("إرسال؟", default=False)},
            disabled=[c for c in filtered_df.columns if c != "Select"],
            hide_index=True,
            use_container_width=True,
            key="local_perfect_matching_grid"
        )
        
        # حصر المختارين بـ علامة صح
        selected_students = edited_df[edited_df["Select"] == True]
        
        # صندوق الإحصاء الذكي
        st.markdown(f"""
            <div style='background-color: #e0f2fe; padding: 15px; border-radius: 8px; margin-top: 15px; border-right: 5px solid #0284c7; text-align: right;'>
                <h4 style='margin: 0; color: #0369a1;'>📊 ملخص أوامر الإرسال المجهزة:</h4>
                <p style='margin: 5px 0 0 0; color: #334155; font-size: 16px;'>عدد الرسائل المحددة التي ستُرسل تلقائياً الآن: <b>{len(selected_students)} رسالة</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        # 🚀 زر بدء الإرسال الجماعي التلقائي
        if st.button("🚀 اضغط هنا لبدء الإرسال الجماعي التلقائي المباشر"):
            if len(selected_students) == 0:
                st.error("الرجاء وضع علامة صح (✓) أمام أسماء الطالبات المراد مراسلتهن أولاً!")
            elif not message_text.strip():
                st.warning("الرجاء كتابة نص الرسالة أولاً!")
            else:
                st.warning("⚠️ تنبيه: سيبدأ بايثون بالإرسال الجماعي التلقائي الآن متتالياً. يرجى إبقاء نافذة الواتساب مفتوحة وعدم تحريك الماوس تماماً.")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                total = len(selected_students)
                
                for index, (idx, row) in enumerate(selected_students.iterrows()):
                    name = str(row[name_col])
                    phone_raw = str(row[phone_col]).strip()
                    
                    # تطهير وتنظيف الرقم من أي رموز مخفية رصدناها في ملفك
                    phone_digits = re.sub(r'\D', '', phone_raw)
                    
                    if phone_digits.startswith("00966"):
                        phone_final = "+" + phone_digits[2:]
                    elif phone_digits.startswith("966"):
                        phone_final = "+" + phone_digits
                    elif phone_digits.startswith("05") and len(phone_digits) == 10:
                        phone_final = "+966" + phone_digits[1:]
                    elif phone_digits.startswith("5") and len(phone_digits) == 9:
                        phone_final = "+966" + phone_digits
                    else:
                        phone_final = "+966" + phone_digits
                    
                    custom_message = message_text.replace("[اسم الطالبة]", name)
                    custom_message = custom_message.replace("[اليوم]", current_day_ar)
                    custom_message = custom_message.replace("[التاريخ الهجري]", hijri_date_str)
                    
                    status_text.text(f"⏳ جاري تجهيز وإرسال الرسالة إلى ولي أمر: {name} ({index + 1}/{total})...")
                    
                    try:
                        kit.sendwhatmsg_instantly(phone_no=phone_final, message=custom_message, wait_time=25, tab_close=True, close_time=3)
                        time.sleep(5)
                        st.success(f"✅ تم الإرسال بنجاح إلى الطالبة: {name}")
                    except Exception as e:
                        st.error(f"❌ فشل الإرسال إلى {name}: {e}")
                        
                    progress_bar.progress((index + 1) / total)
                    
                status_text.text("✅ اكتملت العملية الإجمالية بنجاح، وتم تمرير كافة الأوامر تلقائياً!")
    else:
        st.error(f"❌ خطأ: تأكدي أن ملف الإكسل يحتوي بدقة على الأعمدة التالية بنفس المسمى: '{name_col}'، '{phone_col}'، '{class_col}'")

# --- الحقوق المنسقة أسفل الصفحة ---
st.markdown("""
    <hr style='border-top: 1px solid #bbb;'>
    <div style='display: flex; justify-content: space-between; color: #888; font-size: 14px; direction: rtl;'>
        <div style='font-weight: bold; color: #1E3A8A;'>✨ تصميم واعداد : غادة المجيبل</div>
        <div>نظام الأتمتة المدرسية الحتمي v6.0</div>
    </div>
""", unsafe_allow_html=True)
