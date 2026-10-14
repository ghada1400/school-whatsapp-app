import streamlit as st
import pandas as pd
import urllib.parse
import re
import time
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

st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-right: 5px solid #1E3A8A; text-align: right;'>
        <h2 style='margin: 0; color: #1E3A8A;'>🏫 نظام إدارة ومراسلة الطالبات الإلكتروني السحابي المطور</h2>
        <p style='margin: 5px 0 0 0; color: #555;'>موقع ويب فوري وجاهز للاستخدام دفعة واحدة بمؤقت أمان 10 ثوانٍ وزر انتقال يدوي مأمون</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 اختر ملف إكسل الطالبات (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    name_col = "اسم الطالبة"
    phone_col = "رقم الهاتف"
    class_col = "الصف"

    if name_col in df.columns and phone_col in df.columns and class_col in df.columns:
        
        now = datetime.now()
        current_day_ar = DAYS_ARABIC.get(now.strftime("%A"), now.strftime("%A"))
        hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
        hijri_date_str = f"{hijri_date.day} {HIJRI_MONTHS.get(hijri_date.month, '')} {hijri_date.year} هـ"

        st.markdown("### 📌 تصفية الفصول الدراسيّة")
        df[class_col] = df[class_col].astype(str).str.strip()
        unique_classes = df[class_col].dropna().unique()
        selected_class = st.selectbox("اختر الصف الدراسي:", ["عرض جميع الصفوف"] + list(unique_classes))
        
        filtered_df = df.copy()
        if selected_class != "عرض جميع الصفوف":
            filtered_df = df[df[class_col] == selected_class].copy()

        st.markdown("---")
        st.markdown("### 📝 نص الرسالة الموحدة")
        st.caption(f"💡 الاختصارات: [اسم الطالبة] | [اليوم] ({current_day_ar}) | [التاريخ الهجري] ({hijri_date_str})")
        default_text = "السلام عليكم ولي أمر الطالبة [اسم الطالبة]، نفيدكم علماً بأنه في هذا اليوم [اليوم] الموافق [التاريخ الهجري] قد تم..."
        message_text = st.text_area("تعديل نص الرسالة:", value=default_text, height=100)

        if "Select" not in filtered_df.columns:
            filtered_df.insert(0, "Select", False)

        st.markdown("---")
        st.markdown("### 👥 حدد الطالبات المُراد مراسلتهن من الجدول:")
        st.write(f"📊 عدد الطالبات المتاحات في هذا العرض: **{len(filtered_df)} طالبة**")

        edited_df = st.data_editor(
            filtered_df,
            column_config={"Select": st.column_config.CheckboxColumn("اختيار (✓)", default=False)},
            disabled=[c for c in filtered_df.columns if c != "Select"],
            hide_index=True,
            use_container_width=True,
            key="cloud_perfect_selection_grid_v12_0"
        )
        
        selected_students = edited_df[edited_df["Select"] == True].reset_index(drop=True)
        
        st.markdown(f"""
            <div style='background-color: #e0f2fe; padding: 15px; border-radius: 8px; margin-top: 15px; border-right: 5px solid #0284c7; text-align: right;'>
                <h4 style='margin: 0; color: #0369a1;'>📊 ملخص أوامر الإرسال المجهزة والمجمعة:</h4>
                <p style='margin: 5px 0 0 0; color: #334155; font-size: 16px;'>عدد الرسائل المحددة المتبقية: <b>{len(selected_students)} رسالة</b></p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        # تهيئة متغيرات الذاكرة السحابية
        if "send_index" not in st.session_state:
            st.session_state["send_index"] = 0
        if "start_send" not in st.session_state:
            st.session_state["start_send"] = False
        if "show_countdown" not in st.session_state:
            st.session_state["show_countdown"] = False

        # إنشاء أزرار التحكم بالسيرفر
        col_btn1, col_btn2 = st.columns(2)
        with col_btn2:
            if st.button("🛑 إلغاء وتصفير القائمة فوراً", use_container_width=True):
                st.error("🛑 تم إلغاء تفعيل الجدولة وتصفير النقطة الحالية بنجاح!")
                st.session_state["start_send"] = False
                st.session_state["send_index"] = 0
                st.session_state["show_countdown"] = False
                st.rerun()
                
        with col_btn1:
            if st.button("🚀 اضغط هنا لتفعيل نافذة المراسلة المنظمة للمحدّدات", use_container_width=True):
                st.session_state["start_send"] = True
                st.session_state["send_index"] = 0
                st.session_state["show_countdown"] = False

        st.markdown("### 📲 نافذة الإرسال والتحكم المأمون المجهزة:")
        
        if len(selected_students) == 0:
            st.info("💡 الرجاء وضع علامة صح (✓) أمام أسماء الطالبات في الجدول بالأعلى ليقوم النظام بجمعهن.")
        else:
            if st.session_state["start_send"]:
                total_count = len(selected_students)
                current_idx = st.session_state["send_index"]
                
                if current_idx < total_count:
                    row = selected_students.iloc[current_idx]
                    name = str(row[name_col])
                    phone_raw = str(row[phone_col]).strip()
                    
                    phone_digits = re.sub(r'\D', '', phone_raw)
                    if phone_digits.startswith("00966"): phone_final = phone_digits[5:]
                    elif phone_digits.startswith("966"): phone_final = phone_digits[3:]
                    elif phone_digits.startswith("05"): phone_final = phone_digits[1:]
                    else: phone_final = phone_digits
                        
                    custom_message = message_text.replace("[اسم الطالبة]", name).replace("[اليوم]", current_day_ar).replace("[التاريخ الهجري]", hijri_date_str)
                    encoded_message = urllib.parse.quote(custom_message)
                    
                    base_url = "https://wa.me"
                    phone_and_text = f"966{phone_final}?text={encoded_message}"
                    whatsapp_url = urllib.parse.urljoin(base_url, phone_and_text)
                    
                    st.write(f"👤 **الطالبة الحالية المجهزة للإرسال ({current_idx + 1}/{total_count}):**")
                    
                    # إذا كنا في مرحلة العد التنازلي لحماية الرقم بعد ضغط زر الانتقال
                    if st.session_state["show_countdown"]:
                        st.warning(f"⏱️ جاري تفعيل الحماية والانتظار لمدة (10 ثوانٍ) قبل فتح الاسم التالي لمنع حظر رقم المدرسة...")
                        countdown_box = st.empty()
                        for seconds_left in range(10, 0, -1):
                            countdown_box.metric("⏳ المتبقي لتجهيز الطالبة التالية:", f"{seconds_left} ثانية")
                            time.sleep(1)
                        countdown_box.empty()
                        
                        # إنهاء العد التنازلي وعرض زر الطالبة التالية بسلام
                        st.session_state["show_countdown"] = False
                        st.rerun()
                    else:
                        # عرض زر الواتساب المضمون ويظل ثابتاً حتى تضغطي عليه بنفسكِ براحة تامة
                        st.link_button(f"💬 اضغط الآن لفتح محادثة وإرسال رسالة: {name}", whatsapp_url, use_container_width=True)
                        
                        # زر التأكيد الأخضر للانتقال للامام بعد الاطمئنان من الارسال الحقيقي
                        if current_idx < total_count - 1:
                            st.write("")
                            if st.button(f"➡️ تم الإرسال بنجاح، تفضل بالانتقال للطالبة التالية", use_container_width=True, type="primary"):
                                st.session_state["send_index"] += 1
                                st.session_state["show_countdown"] = True
                                st.rerun()
                        else:
                            st.success("✅ قمتِ بتمرير وإرسال رسائل كافة الأوامر المحددة بنجاح وأمان تام!")
                            
                else:
                    st.success("✅ قمتِ بتمرير وإرسال رسائل كافة الأوامر المحددة بنجاح وأمان تام!")
                    st.session_state["start_send"] = False
                    st.session_state["send_index"] = 0

    else:
        st.error(f"❌ خطأ: تأكدي أن ملف الإكسل يحتوي بدقة على الأعمدة التالية بنفس المسمى: '{name_col}'، '{phone_col}'، '{class_col}'")

# --- الحقوق المنسقة أسفل الصفحة ---
st.markdown("""
    <hr style='border-top: 1px solid #bbb;'>
    <div style='display: flex; justify-content: space-between; color: #888; font-size: 14px; direction: rtl;'>
        <div style='font-weight: bold; color: #1E3A8A;'>✨ تصميم واعداد : غادة Mجيبل</div>
        <div>لوحة تحكم سحابية v12.0 (نسخة التحكم والاتزان المأمون)</div>
    </div>
""", unsafe_allow_html=True)
