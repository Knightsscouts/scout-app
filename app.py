
import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="نظام الفرق الكشفية", layout="centered")
st.title("⚜️ نظام إدارة الفرق الكشفية")

# تحميل البيانات
try:
    df = pd.read_excel("scout_teams.xlsx")
except:
    df = pd.DataFrame(columns=["Team_ID", "Team_Name", "Leader", "Assistants", "Resources", "Balance", "Expiration_Date", "Points", "Penalties"])
    df.to_excel("scout_teams.xlsx", index=False)

# عرض البيانات
st.subheader("📋 قائمة الفرق")
st.dataframe(df)

# إضافة فريق جديد
with st.expander("➕ إضافة فريق"):
    with st.form("add_team"):
        team_id = st.number_input("معرّف الفريق", min_value=1, step=1)
        team_name = st.text_input("اسم الفريق")
        leader = st.text_input("قائد الفريق")
        assistants = st.text_input("المساعدين")
        resources = st.text_input("الموارد (مثلاً: خيم، أدوات)")
        balance = st.number_input("الرصيد", min_value=0, step=1)
        expiration_date = st.date_input("تاريخ انتهاء الرصيد")
        points = st.number_input("النقاط", min_value=0, step=1)
        penalties = st.text_input("العقوبات")
        submitted = st.form_submit_button("إضافة الفريق")
        if submitted:
            new_team = {
                "Team_ID": team_id,
                "Team_Name": team_name,
                "Leader": leader,
                "Assistants": assistants,
                "Resources": resources,
                "Balance": balance,
                "Expiration_Date": expiration_date,
                "Points": points,
                "Penalties": penalties
            }
            df = df.append(new_team, ignore_index=True)
            df.to_excel("scout_teams.xlsx", index=False)
            st.success("✅ تم إضافة الفريق بنجاح!")

# إنشاء QR Code
with st.expander("🔄 إنشاء QR Code لفريق"):
    selected_team = st.selectbox("اختر الفريق", df["Team_Name"])
    if st.button("إنشاء QR Code"):
        team_data = df[df["Team_Name"] == selected_team].to_dict(orient="records")[0]
        qr_info = f"""
        Team: {team_data['Team_Name']}
        Leader: {team_data['Leader']}
        Balance: {team_data['Balance']}
        Points: {team_data['Points']}
        Penalties: {team_data['Penalties']}
        """
        qr = qrcode.make(qr_info)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        st.image(buffer.getvalue(), caption=f"QR Code لفريق {selected_team}")

# استهلاك الموارد
with st.expander("📉 استهلاك الموارد"):
    with st.form("consume_form"):
        team_id = st.number_input("أدخل ID الفريق", min_value=1, step=1, key="consume_id")
        amount = st.number_input("قيمة الاستهلاك", min_value=1, step=1, key="consume_amount")
        if st.form_submit_button("خصم الرصيد"):
            index = df[df["Team_ID"] == team_id].index
            if not index.empty:
                i = index[0]
                df.at[i, "Balance"] = max(0, df.at[i, "Balance"] - amount)
                df.to_excel("scout_teams.xlsx", index=False)
                st.success("✅ تم خصم الموارد بنجاح")
            else:
                st.error("❌ الفريق غير موجود")

# نظام الشحن
with st.expander("💰 شحن الرصيد"):
    with st.form("charge_form"):
        team_id = st.number_input("ID الفريق", min_value=1, step=1, key="charge_id")
        charge_amount = st.number_input("قيمة الشحن", min_value=1, step=1, key="charge_amount")
        points_add = st.number_input("نقاط إضافية", min_value=0, step=1, key="points_add")
        if st.form_submit_button("شحن"):
            index = df[df["Team_ID"] == team_id].index
            if not index.empty:
                i = index[0]
                df.at[i, "Balance"] += charge_amount
                df.at[i, "Points"] += points_add
                df.to_excel("scout_teams.xlsx", index=False)
                st.success("✅ تم الشحن بنجاح")
            else:
                st.error("❌ الفريق غير موجود")

# نظام العقوبات
with st.expander("🚫 تسجيل عقوبة"):
    with st.form("penalty_form"):
        team_id = st.number_input("ID الفريق", min_value=1, step=1, key="penalty_id")
        reason = st.text_input("سبب العقوبة")
        penalty_amount = st.number_input("قيمة العقوبة", min_value=1, step=1, key="penalty_amount")
        if st.form_submit_button("تسجيل العقوبة"):
            index = df[df["Team_ID"] == team_id].index
            if not index.empty:
                i = index[0]
                df.at[i, "Balance"] = max(0, df.at[i, "Balance"] - penalty_amount)
                current_penalties = df.at[i, "Penalties"]
                updated_penalties = f"{current_penalties} | {datetime.now().date()}: {reason} (-{penalty_amount})"
                df.at[i, "Penalties"] = updated_penalties
                df.to_excel("scout_teams.xlsx", index=False)
                st.success("✅ تم تسجيل العقوبة")
            else:
                st.error("❌ الفريق غير موجود")
