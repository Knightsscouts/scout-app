import streamlit as stimport streamlit as st
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
def log_action(action, team_name, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{
        "Timestamp": timestamp,
        "Action": action,
        "Team_Name": team_name,
        "Details": details
    }])
    log_df_updated = pd.concat([log_df, new_log], ignore_index=True)
    log_df_updated.to_excel("team_actions_log.xlsx", index=False)

try:
    inventory_df = pd.read_excel("inventory_items.xlsx")
except FileNotFoundError:
    inventory_df = pd.DataFrame(columns=["Item_Name", "Point_Cost"])
    inventory_df.to_excel("inventory_items.xlsx", index=False)

try:
    log_df = pd.read_excel("team_actions_log.xlsx")
except FileNotFoundError:
    log_df = pd.DataFrame(columns=["Timestamp", "Action", "Team_Name", "Details"])
    log_df.to_excel("team_actions_log.xlsx", index=False)


# الشريط الجانبي
option = st.sidebar.selectbox("القائمة الرئيسية", ["الفرق الكشفية", "تسجيل عهدة", "إدارة العهدة", "QR بيانات الفريق", "📓 سجل الإجراءات", "شحن النقاط"])


# --- الفرق الكشفية ---
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
                st.success("✅ تم إضافة الفريق بنجاح!")
                log_action("إضافة فريق", team_name, f"القائد: {leader}")

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
                        penalty_cost = int(penalties) if penalties.isdigit() else 0  # Assuming penalties are in integer form
                        final_points = points - penalty_cost  # Deduct penalties from points
                        if final_points < 0:
                            final_points = 0  # Prevent points from becoming negative
                        df.at[idx, 'Team_Name'] = team_name
                        df.at[idx, 'Leader'] = leader
                        df.at[idx, 'Assistants'] = assistants
                        df.at[idx, 'Points'] = final_points
                        df.at[idx, 'Penalties'] = "0"  # Clear penalties after deduction
                        df.to_excel("scout_teams.xlsx", index=False)
                        st.success("✅ تم حفظ التعديلات")
                        log_action("تعديل فريق", team_name, f"نقاط: {final_points}, قائد: {leader}")


                if st.button("🗑️ حذف الفريق", key=f"delete_{idx}"):
                    df = df.drop(idx).reset_index(drop=True)
                    df.to_excel("scout_teams.xlsx", index=False)
                    st.warning("⚠️ تم حذف الفريق")
                    log_action("حذف فريق", row["Team_Name"])
                    st.experimental_rerun()

# --- تسجيل عهدة ---
elif option == "تسجيل عهدة":
    st.header("📦 تسجيل عهدة لفريق")
    team_for_loan = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="loan_team")
    item_selected = st.selectbox("اختر العهدة", inventory_df["Item_Name"], key="item_select")
    item_quantity = st.number_input("عدد الوحدات", min_value=1, step=1, value=1)

    if st.button("📤 تأكيد تسليم العهدة"):
        team_index = df[df["Team_Name"] == team_for_loan].index
        if not team_index.empty:
            item_row = inventory_df[inventory_df["Item_Name"] == item_selected]
            if not item_row.empty:
                item_cost = item_row["Point_Cost"].values[0]
                total_cost = item_cost * item_quantity
                idx = team_index[0]
                if df.at[idx, "Points"] >= total_cost:
                    df.at[idx, "Points"] -= total_cost
                    df.at[idx, "Last_Loan"] = f"{item_selected} × {item_quantity} ({datetime.now().date()})"
                    df.to_excel("scout_teams.xlsx", index=False)
                    st.success(f"✅ تم تسليم {item_quantity} × {item_selected} وخصم {total_cost} نقطة")
                    log_action("تسليم عهدة", team_for_loan, f"{item_quantity} × {item_selected} - خصم {total_cost} نقطة")

                else:
                    st.error("❌ الرصيد غير كافٍ")
            else:
                st.error("❌ العهدة غير موجودة")
        else:
            st.error("❌ الفريق غير موجود")



# --- إدارة العهدة ---
elif option == "إدارة العهدة":
    st.header("📁 إدارة أنواع العهدة وتكلفتها")

    with st.form("add_inventory"):
        item_name = st.text_input("اسم العهدة")
        item_cost = st.number_input("تكلفة بالنقاط", min_value=1, step=1)
        submitted_item = st.form_submit_button("➕ إضافة")
        if submitted_item:
            inventory_df = pd.concat([inventory_df, pd.DataFrame([{"Item_Name": item_name, "Point_Cost": item_cost}])], ignore_index=True)
            inventory_df.to_excel("inventory_items.xlsx", index=False)
            st.success("✅ تم إضافة العهدة")

    st.subheader("📋 قائمة العهدة الحالية")
    st.dataframe(inventory_df)

    with st.expander("🗑️ حذف بند عهدة"):
        item_to_delete = st.selectbox("اختر العهدة المراد حذفها", inventory_df["Item_Name"].unique())
        if st.button("حذف العهدة"):
            inventory_df = inventory_df[inventory_df["Item_Name"] != item_to_delete].reset_index(drop=True)
            inventory_df.to_excel("inventory_items.xlsx", index=False)
            st.warning("❌ تم حذف العهدة بنجاح")

# --- QR بيانات الفريق ---
# --- QR بيانات الفريق ---
elif option == "QR بيانات الفريق":
    st.header("📱 عرض بيانات الفريق عبر QR")
    team_qr_select = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="qr_team")
    team_data_df = df[df["Team_Name"] == team_qr_select]

    if not team_data_df.empty:
        team_data = team_data_df.iloc[0]

        # نص البيانات الذي سيتم تحويله إلى QR
        display_text = f"""
        🏷️ اسم الفريق: {team_data['Team_Name']}
        👨‍✈️ القائد: {team_data['Leader']}
        🧑‍🤝‍🧑 المساعدين: {team_data['Assistants']}
        ⭐ النقاط: {team_data['Points']}
        ⛔ العقوبات: {team_data['Penalties']}
        📅 تاريخ انتهاء الرصيد: {team_data['Expiration_Date']}
        🔄 تاريخ آخر شحن: {team_data['Last_Charge_Date']}
        📦 آخر عهدة: {team_data['Last_Loan']}
        """

        # توليد الـ QR الجديد بناءً على النص المحدّث
        qr = qrcode.make(display_text)
        buf = BytesIO()
        qr.save(buf)
        buf.seek(0)

        # عرض صورة الـ QR للمستخدم
        st.image(Image.open(buf), caption="امسح QR لعرض البيانات")

        # عرض بيانات الفريق
        with st.expander("📋 عرض بيانات الفريق"):
            st.text(display_text)

        # زر تحميل الـ QR
        st.download_button(
            label="📥 تحميل QR كصورة",
            data=buf,
            file_name=f"{team_data['Team_Name']}_QR.png",
            mime="image/png"
        )
    else:
        st.warning("⚠️ لم يتم العثور على بيانات للفريق المحدد.")
        # --- سجل الإجراءات ---
elif option == "📓 سجل الإجراءات":
    st.header("📓 سجل كافة الإجراءات على الفرق")

    try:
        log_df = pd.read_excel("team_actions_log.xlsx")

        st.subheader("🔍 تصفية السجل")

        # خيارات التصفية
        team_filter = st.selectbox("اختر الفريق (أو اتركه بلا اختيار لعرض الكل)", [""] + sorted(log_df["Team_Name"].unique()))
        action_filter = st.selectbox("اختر نوع الإجراء (أو اتركه بلا اختيار لعرض الكل)", [""] + sorted(log_df["Action"].unique()))

        # تطبيق التصفية
        filtered_df = log_df.copy()
        if team_filter:
            filtered_df = filtered_df[filtered_df["Team_Name"] == team_filter]
        if action_filter:
            filtered_df = filtered_df[filtered_df["Action"] == action_filter]

        if filtered_df.empty:
            st.info("❗ لا توجد نتائج مطابقة للتصفية.")
        else:
            st.subheader("📋 السجل بعد التصفية")
            for i, row in filtered_df.sort_values(by="Timestamp", ascending=False).iterrows():
                with st.expander(f"🕒 {row['Timestamp']} - {row['Action']} - {row['Team_Name']}"):
                    st.write(f"📌 التفاصيل: {row['Details']}")
                    delete_pin = st.text_input(f"رمز الحذف لإجراء رقم {i}", type="password", key=f"pin_{i}")
                    if st.button(f"🗑️ حذف هذا الإجراء", key=f"del_{i}"):
                        if delete_pin == "12":  # الرقم السري الصحيح
                            # تحديد السطر بدقة
                            original_index = log_df[
                                (log_df["Timestamp"] == row["Timestamp"]) &
                                (log_df["Action"] == row["Action"]) &
                                (log_df["Team_Name"] == row["Team_Name"]) &
                                (log_df["Details"] == row["Details"])
                            ].index
                            if not original_index.empty:
                                log_df = log_df.drop(original_index).reset_index(drop=True)
                                log_df.to_excel("team_actions_log.xlsx", index=False)
                                st.success("✅ تم حذف هذا الإجراء.")
                                st.experimental_rerun()
                        else:
                            st.error("❌ الرقم السري غير صحيح!")

    except:
        st.warning("⚠️ لا يوجد سجل حتى الآن.")


elif option == "شحن النقاط":
    st.header("💳 شحن نقاط الفريق")
    
    # اختر الفريق الذي سيتم شحن نقاطه
    team_for_recharge = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="recharge_team")
    recharge_points = st.number_input("عدد النقاط التي سيتم شحنها", min_value=1, step=1)

    if st.button("📤 شحن النقاط"):
        team_index = df[df["Team_Name"] == team_for_recharge].index
        if not team_index.empty:
            idx = team_index[0]
            # إضافة النقاط
            df.at[idx, "Points"] += recharge_points
            df.at[idx, "Last_Charge_Date"] = datetime.now().date()  # تحديث تاريخ الشحن
            df.to_excel("scout_teams.xlsx", index=False)

            # تأكيد عملية الشحن
            st.success(f"✅ تم شحن {recharge_points} نقطة للفريق {team_for_recharge}")

            # تسجيل السجل الخاص بعملية الشحن
            log_action("شحن نقاط", team_for_recharge, f"تم شحن {recharge_points} نقطة")
        else:
            st.error("❌ الفريق غير موجود")
