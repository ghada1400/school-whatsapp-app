import streamlit as st
import pandas as pd
import urllib.parse
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

st.set_page_config(page_title="نظام مراسلة المدارس المتطور", layout="wide")

st.title("🏫 نظام إدارة ومراسلة الطالبات الذكي بالتقويم الهجري")
st.write("ارفع ملف الإكسل، صفّ الطالبات حسب الصف، حدد الأسماء، وأرسل مباشرة عبر الواتساب.")

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

    if not name_col: name_col = df.columns[0]
    if not phone_col: phone_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    # 🔍 2. ميزة تصفية وفلترة الصفوف
    filtered_df = df.copy()
    if class_col:
        st.write("### 📌 تصفية وحصر الطالبات حسب الصف:")
        df[class_col] = df[class_col].astype(str).str.strip()
        unique_classes = df[class_col].dropna().unique()
        
        selected_class = st.selectbox("اختر الصف لعرض طالباته فقط:", ["عرض جميع الصفوف"] + list(unique_classes))
        
        if selected_class != "عرض جميع الصفوف":
            filtered_df = df[df[class_col] == selected_class].copy()

    st.write("---")
    st.write(f"📊 عدد الطالبات المتاحات في هذا العرض: **{len(filtered_df)}**")
    st.write("### 👥 جدول بيانات الطالبات:")
    st.dataframe(filtered_df)
    
    st.write("---")
    st.write("### 📝 اكتب نص الرسالة الموحدة:")
    
    # 🌙 حساب التاريخ الهجري الحالي بالمكتبة المستقرة
    now = datetime.now()
    current_day_en = now.strftime("%A")
    current_day_ar = DAYS_ARABIC.get(current_day_en, current_day_en)
    
    # التحويل لتقويم أم القرى بشكل آمن ومضمون
    hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
    month_name_ar = HIJRI_MONTHS.get(hijri_date.month, "")
    hijri_date_str = f"{hijri_date.day} {month_name_ar} {hijri_date.year} هـ"
    
    st.info(f"💡 اختصارات ذكية ستتبدل تلقائياً: اكتب `[اسم الطالبة]` أو `[اليوم]` (سيظهر: {current_day_ar}) أو `[التاريخ الهجري]` (سيظهر: {hijri_date_str})")
    
    default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
    message_text = st.text_area("نص الرسالة:", value=default_text)
    
    st.write("### 🚀 روابط المراسلة المباشرة للطالبات:")
    st.write("اضغط على زر الإرسال بجانب اسم كل طالبة لفتح محادثتها بالرسالة المجهزة فوراً:")

    for index, row in filtered_df.iterrows():
        name = str(row[name_col])
        phone = str(row[phone_col]).strip()
        
        # معالجة وإصلاح رقم الهاتف تلقائياً لإضافة رمز الدولة بالسعودية (+966)
        phone = "".join(filter(str.isdigit, phone))
        if phone.startswith("05") and len(phone) == 10:
            phone = "966" + phone[1:]
        elif phone.startswith("5") and len(phone) == 9:
            phone = "966" + phone
            
        custom_message = message_text.replace("[اسم الطالبة]", name)
        custom_message = custom_message.replace("[اليوم]", current_day_ar)
        custom_message = custom_message.replace("[التاريخ الهجري]", hijri_date_str)
        
        # تشفير النص ليكون صالحاً كـ رابط ويب متوافق مع الجوالات والكمبيوتر
        encoded_message = urllib.parse.quote(custom_message)
        whatsapp_url = f"https://whatsapp.com{phone}&text={encoded_message}"
        
        # عرض زر مخصص واحترافي لكل طالبة للإرسال المباشر بضغطة واحدة
        st.link_button(f"📲 إرسال إلى الطالبة: {name}", whatsapp_url)

# --- التوقيع والحقوق أسفل الصفحة ---
st.write("---")
st.markdown("<p style='text-align: right; color: gray; font-weight: bold;'>✨ تصميم واعداد : غادة المجيبل</p>", unsafe_allow_html=True)
