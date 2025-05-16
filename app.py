import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image

# ربط Google Sheets
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="نظام الفرق الكشفية", layout="wide")
st.title("⚜️ مجموعة البشارة المفرحة الكشفية")
st.markdown("""
<h2 style='text-align: center; color: #FFD700;'>سرية العهدة</h2>
""", unsafe_allow_html=True)

# --- إعداد الاتصال بـ Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(credentials)

spreadsheet = client.open("scout_app_data")  # اسم ملف الشيت في Drive
teams_sheet     = spreadsheet.worksheet("teams")
inventory_sheet = spreadsheet.worksheet("inventory")
log_sheet       = spreadsheet.worksheet("logs")

# --- دوال تحميل وحفظ البيانات ---
def load_data():
    df          = pd.DataFrame(teams_sheet.get_all_records())
    inventory_df= pd.DataFrame(inventory_sheet.get_all_records())
    log_df      = pd.DataFrame(log_sheet.get_all_records())
    return df, inventory_df, log_df

def save_data(sheet, dataframe):
    sheet.clear()
    sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

def log_action(log_df, action, team_name, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{
        "Timestamp": timestamp,
        "Action": action,
        "Team_Name": team_name,
        "Details": details
    }])
    log_df = pd.concat([log_df, new_log], ignore_index=True)
    save_data(log_sheet, log_df)
    return log_df

# --- تحميل البيانات مرة واحدة في بداية التشغيل ---
df, inventory_df, log_df = load_data()

# الشريط الجانبي
option = st.sidebar.selectbox("القائمة الرئيسية", [
    "الفرق الكشفية", "تسجيل عهدة", "إدارة العهدة", 
    "QR بيانات الفريق", "📓 سجل الإجراءات", "شحن النقاط"
])

# --- الفرق الكشفية ---
if option == "الفرق الكشفية":
    st.header("📋 إدارة الفرق الكشفية")
    with st.expander("➕ إضافة فريق جديد"):
        with st.form("add_team"):
            team_id        = st.number_input("معرّف الفريق", min_value=1, step=1)
            team_name      = st.text_input("اسم الفريق")
            leader         = st.text_input("قائد الفريق")
            assistants     = st.text_input("المساعدين")
            resources      = st.text_input("الموارد")
            balance        = st.number_input("الرصيد", min_value=0, step=1)
            expiration_date= st.date_input("تاريخ انتهاء الرصيد")
            points         = st.number_input("النقاط", min_value=0, step=1)
            penalties      = st.text_input("العقوبات")
            submitted      = st.form_submit_button("إضافة الفريق")
            if submitted:
                new_team = {
                    "Team_ID": team_id,
                    "Team_Name": team_name,
                    "Leader": leader,
                    "Assistants": assistants,
                    "Resources": resources,
                    "Balance": balance,
                    "Expiration_Date": expiration_date.strftime("%Y-%m-%d"),
                    "Points": points,
                    "Penalties": penalties,
                    "Last_Charge_Date": datetime.now().date().strftime("%Y-%m-%d"),
                    "Last_Loan": "-"
                }
                df = pd.concat([df, pd.DataFrame([new_team])], ignore_index=True)
                save_data(teams_sheet, df)
                log_df = log_action(log_df, "إضافة فريق", team_name, f"القائد: {leader}")
                st.success("✅ تم إضافة الفريق بنجاح!")

    if not df.empty:
        selected = st.selectbox("اختر الفريق لعرض التفاصيل أو التعديل", df["Team_Name"].unique())
        row_df   = df[df["Team_Name"] == selected]
        if not row_df.empty:
            idx = row_df.index[0]
            row = row_df.iloc[0]
            with st.expander(f"📌 الفريق: {row['Team_Name']}"):
                st.write(f"القائد: {row['Leader']}")
                st.write(f"المساعدين: {row['Assistants']}")
                st.write(f"النقاط: {row['Points']}")
                st.write(f"العقوبات: {row['Penalties']}")
                st.write(f"تاريخ انتهاء الرصيد: {row['Expiration_Date']}")
                st.write(f"تاريخ آخر شحن: {row['Last_Charge_Date']}")
                st.write(f"آخر عهدة: {row['Last_Loan']}")

                with st.form(f"edit_team_{idx}"):
                    tname = st.text_input("تعديل الاسم", value=row['Team_Name'])
                    lead  = st.text_input("تعديل القائد", value=row['Leader'])
                    assist= st.text_input("تعديل المساعدين", value=row['Assistants'])
                    pts   = st.number_input("تعديل النقاط", min_value=0, value=int(row['Points']))
                    pen   = st.text_input("تعديل العقوبات", value=row['Penalties'])
                    saveb = st.form_submit_button("💾 حفظ التعديلات")
                    if saveb:
                        pc = int(pen) if pen.isdigit() else 0
                        final_pts = max(pts - pc, 0)
                        df.at[idx, 'Team_Name'] = tname
                        df.at[idx, 'Leader']    = lead
                        df.at[idx, 'Assistants']= assist
                        df.at[idx, 'Points']    = final_pts
                        df.at[idx, 'Penalties'] = "0"
                        save_data(teams_sheet, df)
                        log_df = log_action(log_df, "تعديل فريق", tname, f"نقاط: {final_pts}, قائد: {lead}")
                        st.success("✅ تم حفظ التعديلات")

                if st.button("🗑️ حذف الفريق", key=f"del_{idx}"):
                    df = df.drop(idx).reset_index(drop=True)
                    save_data(teams_sheet, df)
                    log_df = log_action(log_df, "حذف فريق", row["Team_Name"])
                    st.warning("⚠️ تم حذف الفريق")
                    st.experimental_rerun()

# --- تسجيل عهدة ---
elif option == "تسجيل عهدة":
    st.header("📦 تسجيل عهدة لفريق")
    team_for_loan = st.selectbox("اختر الفريق", df["Team_Name"].unique())
    item_selected = st.selectbox("اختر العهدة", inventory_df["Item_Name"])
    qty = st.number_input("عدد الوحدات", min_value=1, step=1, value=1)

    if st.button("📤 تأكيد تسليم العهدة"):
        idxs = df[df["Team_Name"] == team_for_loan].index
        if idxs.any():
            idx = idxs[0]
            row_item = inventory_df[inventory_df["Item_Name"] == item_selected]
            if not row_item.empty:
                cost = row_item["Point_Cost"].values[0]
                total = cost * qty
                if df.at[idx, "Points"] >= total:
                    df.at[idx, "Points"] = df.at[idx, "Points"] - total
                    df.at[idx, "Last_Loan"] = f"{item_selected} × {qty} ({datetime.now().date()})"
                    save_data(teams_sheet, df)
                    log_df = log_action(log_df, "تسليم عهدة", team_for_loan, f"{qty}×{item_selected} - خصم {total} نقطة")
                    st.success(f"✅ تم تسليم {qty}×{item_selected} وخصم {total} نقطة")
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
        item = st.text_input("اسم العهدة")
        cost = st.number_input("تكلفة بالنقاط", min_value=1, step=1)
        addb= st.form_submit_button("➕ إضافة")
        if addb:
            inventory_df = pd.concat([inventory_df, pd.DataFrame([{"Item_Name": item, "Point_Cost": cost}])], ignore_index=True)
            save_data(inventory_sheet, inventory_df)
            st.success("✅ تم إضافة العهدة")
    st.subheader("📋 قائمة العهدة الحالية")
    st.dataframe(inventory_df)
    with st.expander("🗑️ حذف بند عهدة"):
        todel = st.selectbox("اختر بند", inventory_df["Item_Name"].unique())
        if st.button("حذف العهدة"):
            inventory_df = inventory_df[inventory_df["Item_Name"] != todel].reset_index(drop=True)
            save_data(inventory_sheet, inventory_df)
            st.warning("❌ تم حذف العهدة بنجاح")

# --- QR بيانات الفريق ---
elif option == "QR بيانات الفريق":
    st.header("📱 عرض بيانات الفريق عبر QR")
    sel = st.selectbox("اختر الفريق", df["Team_Name"].unique())
    row = df[df["Team_Name"] == sel].iloc[0]
    display_text = f"""
    🏷️ اسم الفريق: {row['Team_Name']}
    👨‍✈️ القائد: {row['Leader']}
    🧑‍🤝‍🧑 المساعدين: {row['Assistants']}
    ⭐ النقاط: {row['Points']}
    ⛔ العقوبات: {row['Penalties']}
    📅 انتهاء الرصيد: {row['Expiration_Date']}
    🔄 آخر شحن: {row['Last_Charge_Date']}
    📦 آخر عهدة: {row['Last_Loan']}
    """
    qr = qrcode.make(display_text)
    buf=BytesIO(); qr.save(buf); buf.seek(0)
    st.image(Image.open(buf), caption="امسح الـQR")
    st.download_button("📥 تحميل QR", data=buf, file_name=f"{sel}_QR.png", mime="image/png")

# --- سجل الإجراءات ---
elif option == "📓 سجل الإجراءات":
    st.header("📓 سجل كافة الإجراءات")
    team_f = st.selectbox("تصفية بالفريق", [""]+sorted(log_df["Team_Name"].unique()))
    act_f  = st.selectbox("تصفية بالإجراء", [""]+sorted(log_df["Action"].unique()))
    filt = log_df.copy()
    if team_f: filt = filt[filt["Team_Name"]==team_f]
    if act_f:  filt = filt[filt["Action"]==act_f]
    for i, r in filt.sort_values(by="Timestamp", ascending=False).iterrows():
        with st.expander(f"{r['Timestamp']} - {r['Action']} - {r['Team_Name']}"):
            st.write(r["Details"])
            pin = st.text_input("رمز الحذف", type="password", key=f"pin_{i}")
            if st.button("🗑️ حذف", key=f"del_{i}"):
                if pin=="12":
                    log_df = log_df.drop(i).reset_index(drop=True)
                    save_data(log_sheet, log_df)
                    st.success("✅ تم الحذف"); st.experimental_rerun()
                else:
                    st.error("❌ رمز خاطئ")

# --- شحن النقاط ---
elif option == "شحن النقاط":
    st.header("💳 شحن نقاط الفريق")
    sel = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="rech")
    pts = st.number_input("عدد النقاط", min_value=1, step=1)
    if st.button("📤 شحن النقاط"):
        idx = df[df["Team_Name"]==sel].index[0]
        df.at[idx,"Points"]+=pts
        df.at[idx,"Last_Charge_Date"]=datetime.now().date().strftime("%Y-%m-%d")
        save_data(teams_sheet, df)
        log_df = log_action(log_df,"شحن نقاط",sel,f"شحن {pts} نقطة")
        st.success("✅ تم الشحن")
