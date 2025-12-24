import streamlit as st
from supabase import create_client, Client

# --- KONFIGURASI SUPABASE ---
URL = "https://bxlfaofmraznomebbrlh.supabase.co"
KEY = "sb_publishable_KuRg1y2stBUHfJshbCUpbg_dvD8s329"
supabase: Client = create_client(URL, KEY)

# --- SETTING HALAMAN ---
st.set_page_config(page_title="IKPA - Master Admin Dashboard", page_icon="⚙️")

# --- INISIALISASI SESSION STATE ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- FUNGSI LOGIKA ---
def fetch_settings():
    try:
        res = supabase.table("settings").select("*").eq("id", 1).single().execute()
        return res.data
    except:
        return None

def push_settings(token, title, theme):
    try:
        supabase.table("settings").update({
            "id_sesi_aktif": token,
            "nama_aplikasi": title,
            "template_aktif": theme
        }).eq("id", 1).execute()
        st.success("🚀 Konfigurasi Berhasil Di-Deploy ke Cloud!")
    except Exception as e:
        st.error(f"Update Gagal: {e}")

# --- UI LOGIC ---

# 1. HALAMAN LOGIN
if not st.session_state.admin_logged_in:
    st.title("🔐 ADMIN ACCESS")
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("LOGIN SYSTEM")
        
        if submit_login:
            if password == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Password Salah!")

# 2. HALAMAN DASHBOARD
else:
    st.title("⚙️ GLOBAL CONTROL")
    st.write("IKPA Master Admin Dashboard")
    
    # Ambil data terbaru dari Supabase
    current_data = fetch_settings()
    
    with st.container():
        st.markdown("### Configuration")
        
        # Input Field
        token_val = st.text_input("ACTIVE SESSION ID (TOKEN)", 
                                  value=current_data.get('id_sesi_aktif', '') if current_data else "")
        
        title_val = st.text_input("CLIENT APP TITLE", 
                                  value=current_data.get('nama_aplikasi', '') if current_data else "")
        
        theme_list = ['dark_teal.xml', 'dark_amber.xml', 'dark_purple.xml', 'light_blue.xml', 'dark_cyan.xml']
        current_theme = current_data.get('template_aktif', 'dark_teal.xml') if current_data else 'dark_teal.xml'
        
        # Cari index tema saat ini untuk default selectbox
        try:
            theme_index = theme_list.index(current_theme)
        except:
            theme_index = 0
            
        theme_val = st.selectbox("VISUAL FRAMEWORK THEME", theme_list, index=theme_index)

        st.divider()
        
        if st.button("🚀 DEPLOY TO CLOUD", use_container_width=True, type="primary"):
            push_settings(token_val, title_val, theme_val)

    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()
