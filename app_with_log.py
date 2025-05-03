import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="نظام الفرق الكشفية", layout="wide")
st.title("⚜️ مجموعة البشارة المفرحة الكشفية")
st.markdown("""
<h2 style='text-align: center; color: #FFD700;'>سرية العهدة</h2>
""", unsafe_allow_html=True)

# تحميل البيانات
try:
    df = pd.read_excel("scout_teams.xlsx")
except:
    df = pd.DataFrame(columns=[
        "Team_ID", "Team_Name", "Leader", "Assistants", "Resources",
        "Balance", "Expiration_Date", "Points", "Penalties",
        "Last_Charge_Date", "Last_Loan"
    ])
    df.to_excel("scout_teams.xlsx", index=False)

try:
    inventory_df = pd.read_excel("inventory_items.xlsx")
except:
    inventory_df = pd.DataFrame(columns=["Item_Name", "Point_Cost"])
    inventory_df.to_excel("inventory_items.xlsx", index=False)

try:
    log_df = pd.read_excel("team_actions_log.xlsx")
except:
    log_df = pd.DataFrame(columns=["Timestamp", "Team_Name", "Action", "Details"])
    log_df.to_excel("team_actions_log.xlsx", index=False)

option = st.sidebar.selectbox("القائمة الرئيسية", ["الفرق الكشفية", "تسجيل عهدة", "إدارة العهدة", "QR بيانات الفريق"])

if option == "الفرق الكشفية":
    st.header("📋 إدارة الفرق الكشفية")
    with st.expander("➕ إضافة فريق جديد"):
        with st.form("add_team"):
            team_id = st.number_input("معرّف الفريق", min_value=1, step=1)
            team_name = st.text_input("اسم الفريق")
            leader = st.text_input("قائد الفريق")
            assistants = st.text_input("المساعدين")
            resources = st.text_input("الموارد")
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
                    "Penalties": penalties,
                    "Last_Charge_Date": datetime.now().date(),
                    "Last_Loan": "-"
                }
                df = pd.concat([df, pd.DataFrame([new_team])], ignore_index=True)
                df.to_excel("scout_teams.xlsx", index=False)

                log_df = pd.concat([log_df, pd.DataFrame([{
                    "Timestamp": datetime.now(),
                    "Team_Name": team_name,
                    "Action": "إضافة فريق",
                    "Details": f"تمت إضافة الفريق: {team_name}"
                }])], ignore_index=True)
                log_df.to_excel("team_actions_log.xlsx", index=False)

                st.success("✅ تم إضافة الفريق بنجاح!")

    if not df.empty:
        selected_team_view = st.selectbox("اختر الفريق لعرض التفاصيل أو التعديل", df["Team_Name"].unique())
        team_row = df[df["Team_Name"] == selected_team_view]
        if not team_row.empty:
            idx = team_row.index[0]
            row = team_row.iloc[0]

            with st.expander(f"📌 الفريق: {row['Team_Name']}"):
                st.write(f"القائد: {row['Leader']}")
                st.write(f"المساعدين: {row['Assistants']}")
                st.write(f"النقاط: {row['Points']}")
                st.write(f"العقوبات: {row['Penalties']}")
                st.write(f"تاريخ انتهاء الرصيد: {row['Expiration_Date']}")
                st.write(f"تاريخ آخر شحن: {row['Last_Charge_Date']}")
                st.write(f"آخر عهدة: {row['Last_Loan']}")

                with st.form(f"edit_team_{idx}"):
                    team_name = st.text_input("تعديل الاسم", value=row['Team_Name'])
                    leader = st.text_input("تعديل القائد", value=row['Leader'])
                    assistants = st.text_input("تعديل المساعدين", value=row['Assistants'])
                    points = st.number_input("تعديل النقاط", min_value=0, value=int(row['Points']))
                    penalties = st.text_input("تعديل العقوبات", value=row['Penalties'])
                    submitted_edit = st.form_submit_button("💾 حفظ التعديلات")
                    if submitted_edit:
                        penalty_cost = int(penalties) if penalties.isdigit() else 0
                        final_points = max(points - penalty_cost, 0)
                        df.at[idx, 'Team_Name'] = team_name
                        df.at[idx, 'Leader'] = leader
                        df.at[idx, 'Assistants'] = assistants
                        df.at[idx, 'Points'] = final_points
                        df.at[idx, 'Penalties'] = "0"
                        df.to_excel("scout_teams.xlsx", index=False)

                        log_df = pd.concat([log_df, pd.DataFrame([{
                            "Timestamp": datetime.now(),
                            "Team_Name": team_name,
                            "Action": "تعديل بيانات",
                            "Details": f"تم تعديل الفريق: {team_name}"
                        }])], ignore_index=True)
                        log_df.to_excel("team_actions_log.xlsx", index=False)

                        st.success("✅ تم حفظ التعديلات")

                if st.button("🗑️ حذف الفريق", key=f"delete_{idx}"):
                    team_name = df.at[idx, 'Team_Name']
                    df = df.drop(idx).reset_index(drop=True)
                    df.to_excel("scout_teams.xlsx", index=False)

                    log_df = pd.concat([log_df, pd.DataFrame([{
                        "Timestamp": datetime.now(),
                        "Team_Name": team_name,
                        "Action": "حذف فريق",
                        "Details": f"تم حذف الفريق: {team_name}"
                    }])], ignore_index=True)
                    log_df.to_excel("team_actions_log.xlsx", index=False)

                    st.warning("⚠️ تم حذف الفريق")
                    st.experimental_rerun()

elif option == "تسجيل عهدة":
    st.header("📦 تسجيل عهدة لفريق")
    team_for_loan = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="loan_team")
    item_selected = st.selectbox("اختر العهدة", inventory_df["Item_Name"], key="item_select")
    item_quantity = st.number_input("الكمية", min_value=1, value=1, step=1)

    if st.button("📤 تأكيد تسليم العهدة"):
        team_index = df[df["Team_Name"] == team_for_loan].index
        if not team_index.empty:
            item_cost = inventory_df[inventory_df["Item_Name"] == item_selected]["Point_Cost"].values[0]
            total_cost = item_cost * item_quantity
            idx = team_index[0]
            if df.at[idx, "Points"] >= total_cost:
                df.at[idx, "Points"] -= total_cost
                df.at[idx, "Last_Loan"] = f"{item_selected} × {item_quantity} ({datetime.now().date()})"
                df.to_excel("scout_teams.xlsx", index=False)

                log_df = pd.concat([log_df, pd.DataFrame([{
                    "Timestamp": datetime.now(),
                    "Team_Name": df.at[idx, "Team_Name"],
                    "Action": "تسليم عهدة",
                    "Details": f"تم تسليم {item_quantity} × {item_selected} وخصم {total_cost} نقطة"
                }])], ignore_index=True)
                log_df.to_excel("team_actions_log.xlsx", index=False)

                st.success(f"✅ تم تسليم {item_quantity} × {item_selected} وخصم {total_cost} نقطة")
            else:
                st.error("❌ الرصيد غير كافٍ")
        else:
            st.error("❌ الفريق غير موجود")