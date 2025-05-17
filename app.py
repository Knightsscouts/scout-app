from supabase import create_client, Client

# بيانات الدخول الخاصة بمشروع Supabase بتاعك
url: str = "https://aembrtkzmiijydugyfhj.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlbWJydGt6bWlpanlkdWd5ZmhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0NzA2OTcsImV4cCI6MjA2MzA0NjY5N30.whD0YcVBMZ6hRd5QDtiNyGYGe5OUFwOfa1x4fuX2w9w"

supabase: Client = create_client(url, key)
def log_action(action, table_name, description, team_id):
    data = {
        "action": action,
        "table_name": table_name,
        "description": description,
        "team_id": team_id
    }
    supabase.table("action_log").insert(data).execute()

import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image
from supabase import create_client, Client

# Supabase setup
supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.set_page_config(page_title="نظام الفرق الكشفية", layout="wide")
st.title("⚜ مجموعة البشارة المفرحة الكشفية")
st.markdown("""
<h2 style='text-align: center; color: #FFD700;'>سرية العهدة</h2>
""", unsafe_allow_html=True)

# Database functions
def get_teams():
    response = supabase.table('teams').select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def get_inventory():
    response = supabase.table('inventory').select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def get_logs():
    response = supabase.table('action_logs').select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def log_action(action, team_name, details=""):
    supabase.table('action_logs').insert({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "team_name": team_name,
        "details": details
    }).execute()

# Load data from Supabase
try:
    df = get_teams()
    inventory_df = get_inventory()
    log_df = get_logs()
except Exception as e:
    st.error(f"Error connecting to database: {str(e)}")
    df = pd.DataFrame()
    inventory_df = pd.DataFrame()
    log_df = pd.DataFrame()

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
                    "Expiration_Date": expiration_date.isoformat(),
                    "Points": points,
                    "Penalties": penalties,
                    "Last_Charge_Date": datetime.now().date().isoformat(),
                    "Last_Loan": "-"
                }
                supabase.table('teams').insert(new_team).execute()
                st.success("✅ تم إضافة الفريق بنجاح!")
                log_action("إضافة فريق", team_name, f"القائد: {leader}")
                df = get_teams()

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
                        final_points = points - penalty_cost
                        if final_points < 0:
                            final_points = 0
                        supabase.table('teams').update({
                            'Team_Name': team_name,
                            'Leader': leader,
                            'Assistants': assistants,
                            'Points': final_points,
                            'Penalties': "0"
                        }).eq('Team_ID', row['Team_ID']).execute()
                        st.success("✅ تم حفظ التعديلات")
                        log_action("تعديل فريق", team_name, f"نقاط: {final_points}, قائد: {leader}")
                        df = get_teams()

                if st.button("🗑 حذف الفريق", key=f"delete_{idx}"):
                    supabase.table('teams').delete().eq('Team_ID', row['Team_ID']).execute()
                    st.warning("⚠ تم حذف الفريق")
                    log_action("حذف فريق", row["Team_Name"])
                    df = get_teams()
                    st.experimental_rerun()

# --- تسجيل عهدة ---
elif option == "تسجيل عهدة":
    st.header("📦 تسجيل عهدة لفريق")
    team_for_loan = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="loan_team")
    item_selected = st.selectbox("اختر العهدة", inventory_df["Item_Name"], key="item_select")
    item_quantity = st.number_input("عدد الوحدات", min_value=1, step=1, value=1)

    if st.button("📤 تأكيد تسليم العهدة"):
        team_row = df[df["Team_Name"] == team_for_loan]
        if not team_row.empty:
            item_row = inventory_df[inventory_df["Item_Name"] == item_selected]
            if not item_row.empty:
                item_cost = item_row["Point_Cost"].values[0]
                total_cost = item_cost * item_quantity
                team_points = team_row.iloc[0]["Points"]
                
                if team_points >= total_cost:
                    new_points = team_points - total_cost
                    supabase.table('teams').update({
                        'Points': new_points,
                        'Last_Loan': f"{item_selected} × {item_quantity} ({datetime.now().date()})"
                    }).eq('Team_ID', team_row.iloc[0]['Team_ID']).execute()
                    
                    st.success(f"✅ تم تسليم {item_quantity} × {item_selected} وخصم {total_cost} نقطة")
                    log_action("تسليم عهدة", team_for_loan, f"{item_quantity} × {item_selected} - خصم {total_cost} نقطة")
                    df = get_teams()
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
            supabase.table('inventory').insert({
                "Item_Name": item_name,
                "Point_Cost": item_cost
            }).execute()
            st.success("✅ تم إضافة العهدة")
            inventory_df = get_inventory()

    st.subheader("📋 قائمة العهدة الحالية")
    st.dataframe(inventory_df)

    with st.expander("🗑 حذف بند عهدة"):
        item_to_delete = st.selectbox("اختر العهدة المراد حذفها", inventory_df["Item_Name"].unique())
        if st.button("حذف العهدة"):
            supabase.table('inventory').delete().eq('Item_Name', item_to_delete).execute()
            st.warning("❌ تم حذف العهدة بنجاح")
            inventory_df = get_inventory()

# --- QR بيانات الفريق ---
elif option == "QR بيانات الفريق":
    st.header("📱 عرض بيانات الفريق عبر QR")
    team_qr_select = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="qr_team")
    team_data_df = df[df["Team_Name"] == team_qr_select]

    if not team_data_df.empty:
        team_data = team_data_df.iloc[0]

        display_text = f"""
        🏷 اسم الفريق: {team_data['Team_Name']}
        👨‍✈ القائد: {team_data['Leader']}
        🧑‍🤝‍🧑 المساعدين: {team_data['Assistants']}
        ⭐ النقاط: {team_data['Points']}
        ⛔ العقوبات: {team_data['Penalties']}
        📅 تاريخ انتهاء الرصيد: {team_data['Expiration_Date']}
        🔄 تاريخ آخر شحن: {team_data['Last_Charge_Date']}
        📦 آخر عهدة: {team_data['Last_Loan']}
        """

        qr = qrcode.make(display_text)
        buf = BytesIO()
        qr.save(buf)
        buf.seek(0)

        st.image(Image.open(buf), caption="امسح QR لعرض البيانات")

        with st.expander("📋 عرض بيانات الفريق"):
            st.text(display_text)

        st.download_button(
            label="📥 تحميل QR كصورة",
            data=buf,
            file_name=f"{team_data['Team_Name']}_QR.png",
            mime="image/png"
        )
    else:
        st.warning("⚠ لم يتم العثور على بيانات للفريق المحدد.")

# --- سجل الإجراءات ---
elif option == "📓 سجل الإجراءات":
    st.header("📓 سجل كافة الإجراءات على الفرق")

    try:
        log_df = get_logs()

        st.subheader("🔍 تصفية السجل")

        team_filter = st.selectbox("اختر الفريق (أو اتركه بلا اختيار لعرض الكل)", [""] + sorted(log_df["team_name"].unique()))
        action_filter = st.selectbox("اختر نوع الإجراء (أو اتركه بلا اختيار لعرض الكل)", [""] + sorted(log_df["action"].unique()))

        filtered_df = log_df.copy()
        if team_filter:
            filtered_df = filtered_df[filtered_df["team_name"] == team_filter]
        if action_filter:
            filtered_df = filtered_df[filtered_df["action"] == action_filter]

        if filtered_df.empty:
            st.info("❗ لا توجد نتائج مطابقة للتصفية.")
        else:
            st.subheader("📋 السجل بعد التصفية")
            for i, row in filtered_df.sort_values(by="timestamp", ascending=False).iterrows():
                with st.expander(f"🕒 {row['timestamp']} - {row['action']} - {row['team_name']}"):
                    st.write(f"📌 التفاصيل: {row['details']}")
                    delete_pin = st.text_input(f"رمز الحذف لإجراء رقم {i}", type="password", key=f"pin_{i}")
                    if st.button(f"🗑 حذف هذا الإجراء", key=f"del_{i}"):
                        if delete_pin == "12":
                            supabase.table('action_logs').delete().eq('id', row['id']).execute()
                            st.success("✅ تم حذف هذا الإجراء.")
                            log_df = get_logs()
                            st.experimental_rerun()
                        else:
                            st.error("❌ الرقم السري غير صحيح!")

    except Exception as e:
        st.warning(f"⚠ خطأ في تحميل السجل: {str(e)}")

# --- شحن النقاط ---
elif option == "شحن النقاط":
    st.header("💳 شحن نقاط الفريق")
    
    team_for_recharge = st.selectbox("اختر الفريق", df["Team_Name"].unique(), key="recharge_team")
    recharge_points = st.number_input("عدد النقاط التي سيتم شحنها", min_value=1, step=1)

    if st.button("📤 شحن النقاط"):
        team_row = df[df["Team_Name"] == team_for_recharge]
        if not team_row.empty:
            current_points = team_row.iloc[0]["Points"]
            new_points = current_points + recharge_points
            
            supabase.table('teams').update({
                'Points': new_points,
                'Last_Charge_Date': datetime.now().date().isoformat()
            }).eq('Team_ID', team_row.iloc[0]['Team_ID']).execute()

            st.success(f"✅ تم شحن {recharge_points} نقطة للفريق {team_for_recharge}")
            log_action("شحن نقاط", team_for_recharge, f"تم شحن {recharge_points} نقطة")
            df = get_teams()
        else:
            st.error("❌ الفريق غير موجود")
