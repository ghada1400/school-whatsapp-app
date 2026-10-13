import streamlit as st
import pandas as pd
import pywhatkit as kit
import time
from datetime import datetime
from hijri_converter import Gregorian

# إعداد وتغيير أسماء الأيام والشهور الهجرية للعربية
DAYS_ARABIC = {
    "Monday": "الاثنين",
    "Tuesday": "الثلاثاء",
    "Wednesday": "الأربعاء",
    "Thursday": "الخميس",
    "Friday": "الجمعة",
    "Saturday": "السبت",
    "Sunday": "الأحد"
}

HIJRI_MONTHS = {
    1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الثاني",
    5: "جمادى الأولى", 6: "جمادى الآخرة", 7: "رجب", 8: "شعبان",
    9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة"
}

st.set_page_config(page_title="نظام مراسلة المدارس - غادة المجيبل", layout="wide")

st.title("🏫 نظام إدارة ومراسلة الطالبات الذكي بالتقويم الهجري")
st.write("ارفع ملف الإكسل، صفّ الطالبات حسب الصف، حدد الأسماء، وأرسل تلقائياً مع الاسم واليوم والتاريخ الهجري.")

# 📂 1. رفع ملف الإكسل
uploaded_file = st.file_uploader("اختر ملف إكسل الطالبات (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip() # تنظيف الأعمدة من المسافات
    
    st.success("تم تحميل بيانات الملف بنجاح!")
    
    # ⚙️ محاولة التعرف التلقائي الذكي على الأعمدة
    name_col = None
    phone_col = None
    class_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if "اسم" in col_lower or "name" in col_lower:
            name_col = col
        elif "جوال" in col_lower or "هاتف" in col_lower or "رقم" in col_lower or "phone" in col_lower or "mobile" in col_lower:
            phone_col = col
        elif "صف" in col_lower or "فصل" in col_lower or "class" in col_lower or "المرحلة" in col_lower:
            class_col = col

    if not name_col: name_col = df.columns
    if not phone_col: phone_col = df.columns if len(df.columns) > 1 else df.columns

    # 🔍 2. ميزة تصفية وفلترة الصفوف
    filtered_df = df.copy()
    if class_col:
        st.write("### 📌 تصفية وحصر الطالبات حسب الصف:")
        df[class_col] = df[class_col].astype(str).str.strip()
        unique_classes = df[class_col].dropna().unique()
        
        selected_class = st.selectbox("اختر الصف لعرض طالباته فقط:", ["عرض جميع الصفوف"] + list(unique_classes))
        
        if selected_class != "عرض جميع الصفوف":
            filtered_df = df[df[class_col] == selected_class].copy()

    # إضافة عمود الاختيار للجدول المفلتر
    if "Select" not in filtered_df.columns:
        filtered_df.insert(0, "Select", False)

    st.write("---")
    st.write(f"📊 عدد الطالبات المتاحات في هذا العرض: **{len(filtered_df)}**")
    st.write("### 👥 ضع علامة (✓) أمام الطالبات المراد مراسلتهن:")
    
    # عرض الجدول التفاعلي
    edited_df = st.data_editor(
        filtered_df,
        column_config={"Select": st.column_config.CheckboxColumn("اختيار", default=False)},
        disabled=[c for c in filtered_df.columns if c != "Select"],
        key="students_final_hijri_prod_editor"
    )
    
    selected_students = edited_df[edited_df["Select"] == True]
    
    st.write("---")
    st.write("### 📝 اكتب نص الرسالة الموحدة:")
    
    # 🌙 حساب التاريخ الهجري الحالي بالمكتبة الجديدة المستقرة
    now = datetime.now()
    current_day_en = now.strftime("%A")
    current_day_ar = DAYS_ARABIC.get(current_day_en, current_day_en)
    
    # التحويل لتقويم أم القرى بشكل آمن ومضمون
    hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
    month_name_ar = HIJRI_MONTHS.get(hijri_date.month, "")
    hijri_date_str = f"{hijri_date.day} {month_name_ar} {hijri_date.year} هـ"
    
    st.info(f"💡 اختصارات ذكية ستتبدل تلقائياً: اكتب `[اسم الطالبة]` أو `[اليوم]` (سيظهر: {current_day_ar}) أو `[التاريخ الهجري]` (سيظهر: {hijri_date_str})")
    
    # مربع النص الافتراضي بالصيغة الهجرية
    default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
    message_text = st.text_area("نص الرسالة:", value=default_text)
    
    st.write(f"🎯 عدد الطالبات المحددات للإرسال الفعلي: **{len(selected_students)}**")
    
    # 🚀 3. زر بدء الإرسال التلقائي
    if st.button("اضغط هنا لبدء الإرسال التلقائي المباشر لجميع المختارين"):
        if len(selected_students) == 0:
            st.error("الرجاء اختيار طالبة واحدة على الأقل من الجدول بالأعلى!")
        elif not message_text.strip():
            st.warning("الرجاء كتابة نص الرسالة أولاً!")
        else:
            st.warning("⚠️ انتظر قليلاً.. سيبدأ الإرسال التلقائي الآن. يرجى إبقاء المتصفح مفتوحاً وعدم تحريك الماوس.")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            total = len(selected_students)
            
            for index, (idx, row) in enumerate(selected_students.iterrows()):
                name = str(row[name_col])
                phone = str(row[phone_col]).strip()
                
                # إصلاح وتعديل صيغة رقم الهاتف الدولية
                phone = "".join(filter(str.isdigit, phone))
                if phone.startswith("05") and len(phone) == 10:
                    phone = "+966" + phone[1:]
                elif phone.startswith("5") and len(phone) == 9:
                    phone = "+966" + phone
                elif phone.startswith("966") and len(phone) == 12:
                    phone = "+" + phone
                
                # 🔄 التبديل الديناميكي لكل رسالة
                custom_message = message_text.replace("[اسم الطالبة]", name)
                custom_message = custom_message.replace("[اليوم]", current_day_ar)
                custom_message = custom_message.replace("[التاريخ الهجري]", hijri_date_str)
                
                status_text.text(f"⏳ جاري تجهيز وإرسال الرسالة إلى: {name} ({index + 1}/{total})...")
                
                try:
                    kit.sendwhatmsg_instantly(phone_no=phone, message=custom_message, wait_time=25, tab_close=True, close_time=3)
                    time.sleep(5) # وقت أمان بين الرسائل
                    st.success(f"✅ تمت جدولة وإرسال الرسالة بنجاح إلى: {name}")
                except Exception as e:
                    st.error(f"❌ فشل الإرسال إلى {name}: {e}")
                    
                progress_bar.progress((index + 1) / total)
                
            status_text.text("✅ اكتملت العملية وتم تمرير كافة الرسائل المحددة!")

