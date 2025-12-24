import streamlit as st
from supabase import create_client, Client
import time

# --- KONFIGURASI SUPABASE ---
URL = "https://bxlfaofmraznomebbrlh.supabase.co"
KEY = "sb_publishable_KuRg1y2stBUHfJshbCUpbg_dvD8s329"
supabase: Client = create_client(URL, KEY)

# --- FUNGSI AMBIL KONFIGURASI ---
def get_cloud_config():
    try:
        r = supabase.table("settings").select("*").eq("id", 1).single().execute()
        return r.data.get('id_sesi_aktif', '113'), r.data.get('nama_aplikasi', 'IKPA Quiz')
    except:
        return "113", "IKPA Quiz"

TOKEN_CORRECT, APP_TITLE = get_cloud_config()

# --- INISIALISASI SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "TOKEN"
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'identity' not in st.session_state:
    st.session_state.identity = ""

st.set_page_config(page_title=APP_TITLE, page_icon="📝")

# --- LOGIKA ANTARMUKA ---

# 1. HALAMAN TOKEN
if st.session_state.page == "TOKEN":
    st.title("🔐 MASUKKAN TOKEN SESI")
    token_input = st.text_input("Token / ID Sesi", type="password")
    if st.button("VERIFIKASI"):
        if token_input == TOKEN_CORRECT:
            st.session_state.page = "LOGIN"
            st.rerun()
        else:
            st.error("Token Sesi Salah!")

# 2. HALAMAN LOGIN
elif st.session_state.page == "LOGIN":
    st.title("IDENTITAS PESERTA")
    nama = st.text_input("Nama Lengkap")
    nim = st.text_input("NRP/NIM")
    if st.button("MULAI KUIS"):
        if nama and nim:
            st.session_state.identity = f"{nama} ({nim})"
            # Load soal dari Supabase
            try:
                res = supabase.table("QUIS").select("*").execute()
                st.session_state.data_soal = res.data
                st.session_state.page = "QUIZ"
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memuat soal: {e}")
        else:
            st.warning("Isi identitas lengkap!")

# 3. HALAMAN KUIS
elif st.session_state.page == "QUIZ":
    soal_list = st.session_state.data_soal
    idx = st.session_state.current_index
    
    if idx < len(soal_list):
        soal = soal_list[idx]
        st.progress((idx) / len(soal_list))
        st.subheader(f"Soal {idx + 1}")
        st.info(soal['Pertanyaan'])
        
        options = soal['Pilihan_Jawaban']
        # Mapping pilihan agar rapi
        choice = st.radio("Pilih Jawaban:", list(options.values()), key=f"q_{idx}")
        
        if st.button("KONFIRMASI JAWABAN"):
            # Cari kunci (a, b, c, d) dari nilai yang dipilih
            user_key = [k for k, v in options.items() if v == choice][0]
            if user_key.lower() == soal['Jawaban_Benar'].lower():
                st.session_state.score += 10
            
            st.session_state.current_index += 1
            st.rerun()
    else:
        st.session_state.page = "RESULT"
        st.rerun()

# 4. HALAMAN HASIL & LEADERBOARD
elif st.session_state.page == "RESULT":
    st.title("🏁 HASIL KUIS")
    st.balloons()
    st.success(f"Skor Akhir Anda: {st.session_state.score}")
    
    if st.button("SUBMIT KE LEADERBOARD"):
        data = {
            'nama': st.session_state.identity, 
            'skor': st.session_state.score, 
            'id_sesi': TOKEN_CORRECT, 
            'tanggal_waktu': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        supabase.table("skor").insert(data).execute()
        st.info("Skor Anda telah berhasil disubmit!")
    
    st.divider()
    st.subheader("🏆 Leaderboard (Top 5)")
    res_ld = supabase.table("skor").select("nama,skor").eq("id_sesi", TOKEN_CORRECT).order("skor", desc=True).limit(5).execute()
    if res_ld.data:
        st.table(res_ld.data)
    
    if st.button("Ulangi Kuis"):
        st.session_state.clear()
        st.rerun()
