import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QMessageBox, QStackedWidget, QProgressBar, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from supabase import create_client, Client
from qt_material import apply_stylesheet

URL = "https://bxlfaofmraznomebbrlh.supabase.co"
KEY = "sb_publishable_KuRg1y2stBUHfJshbCUpbg_dvD8s329"
supabase: Client = create_client(URL, KEY)

class ClientQuizApp(QMainWindow):
    def __init__(self, token_correct, title):
        super().__init__()
        self.TOKEN_CLOUD = token_correct
        self.setWindowTitle(title)
        self.setFixedSize(550, 750)

        self.data_soal = []; self.index = 0; self.score = 0; self.identity = ""
        self.stack = QStackedWidget(); self.setCentralWidget(self.stack)

        self.setup_token_page() # Index 0
        self.setup_login()      # Index 1
        self.setup_quiz()       # Index 2
        self.setup_result()     # Index 3

    def setup_token_page(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setAlignment(Qt.AlignCenter); lay.setSpacing(20)
        header = QLabel("🔐 MASUKKAN TOKEN SESI"); header.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffb300;")
        lay.addWidget(header, alignment=Qt.AlignCenter)
        self.in_token = QLineEdit(); self.in_token.setPlaceholderText("Token / ID Sesi"); self.in_token.setFixedWidth(300); self.in_token.setFixedHeight(45); self.in_token.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.in_token, alignment=Qt.AlignCenter)
        btn = QPushButton("VERIFIKASI"); btn.setFixedHeight(50); btn.setFixedWidth(150); btn.clicked.connect(self.check_token)
        lay.addWidget(btn, alignment=Qt.AlignCenter); self.stack.addWidget(page)

    def check_token(self):
        if self.in_token.text().strip() == self.TOKEN_CLOUD: self.stack.setCurrentIndex(1)
        else: QMessageBox.critical(self, "Gagal", "Token Sesi Salah!")

    def setup_login(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setAlignment(Qt.AlignCenter); lay.setSpacing(20)
        header = QLabel("IDENTITAS PESERTA"); header.setStyleSheet("font-size: 22px; font-weight: bold; color: #00bcd4;")
        lay.addWidget(header, alignment=Qt.AlignCenter)
        self.in_nama = QLineEdit(); self.in_nama.setPlaceholderText("Nama Lengkap"); self.in_nim = QLineEdit(); self.in_nim.setPlaceholderText("NRP/NIM")
        self.in_nama.setFixedWidth(350); self.in_nim.setFixedWidth(350); self.in_nama.setFixedHeight(45); self.in_nim.setFixedHeight(45)
        lay.addWidget(self.in_nama, alignment=Qt.AlignCenter); lay.addWidget(self.in_nim, alignment=Qt.AlignCenter)
        btn = QPushButton("MULAI KUIS"); btn.clicked.connect(self.start_session)
        lay.addWidget(btn, alignment=Qt.AlignCenter); self.stack.addWidget(page)

    def start_session(self):
        if self.in_nama.text().strip() and self.in_nim.text().strip():
            self.identity = f"{self.in_nama.text()} ({self.in_nim.text()})"
            self.load_questions()
        else: QMessageBox.warning(self, "Peringatan", "Isi identitas lengkap!")

    def load_questions(self):
        try:
            res = supabase.table("QUIS").select("*").execute()
            self.data_soal = res.data
            if self.data_soal: self.show_question(); self.stack.setCurrentIndex(2)
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def setup_quiz(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(30,30,30,30)
        self.prog = QProgressBar(); self.prog.setFixedHeight(10); lay.addWidget(self.prog)
        self.lbl_q = QLabel("Memuat..."); self.lbl_q.setWordWrap(True); self.lbl_q.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px 0;"); lay.addWidget(self.lbl_q)
        self.btn_grp = QButtonGroup(self); self.radios = []
        for i in range(4):
            r = QRadioButton("-"); r.setStyleSheet("padding: 10px; font-size: 14px;"); self.radios.append(r); self.btn_grp.addButton(r, i); lay.addWidget(r)
        lay.addStretch(); btn = QPushButton("KONFIRMASI JAWABAN"); btn.setFixedHeight(60); btn.clicked.connect(self.check_ans); lay.addWidget(btn)
        self.stack.addWidget(page)

    def show_question(self):
        q = self.data_soal[self.index]
        self.lbl_q.setText(f"Soal {self.index+1}:\n\n{q['Pertanyaan']}")
        p = q['Pilihan_Jawaban']; keys = sorted(p.keys())
        for i, k in enumerate(keys):
            if i < len(self.radios): self.radios[i].setText(f"{k.upper()}. {p[k]}"); self.radios[i].setProperty("k", k.lower())
        self.prog.setValue(int((self.index/len(self.data_soal))*100))

    def check_ans(self):
        sel = self.btn_grp.checkedButton()
        if not sel: return
        if sel.property("k") == self.data_soal[self.index]['Jawaban_Benar'].lower(): self.score += 10
        self.index += 1
        if self.index < len(self.data_soal): self.show_question()
        else: self.stack.setCurrentIndex(3); self.final_page()

    def setup_result(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setAlignment(Qt.AlignCenter)
        self.lbl_res = QLabel("Skor: 0"); self.lbl_res.setStyleSheet("font-size: 30px; font-weight: bold; color: #4caf50;"); lay.addWidget(self.lbl_res, alignment=Qt.AlignCenter)
        self.btn_sync = QPushButton("SUBMIT KE LEADERBOARD"); self.btn_sync.setFixedHeight(55); self.btn_sync.setFixedWidth(300); self.btn_sync.clicked.connect(self.sync); lay.addWidget(self.btn_sync, alignment=Qt.AlignCenter)
        self.tab = QTableWidget(0,3); self.tab.setHorizontalHeaderLabels(["Rank","Nama","Skor"]); self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); lay.addWidget(self.tab)
        self.stack.addWidget(page)

    def final_page(self): self.lbl_res.setText(f"Skor Akhir: {self.score}")

    def sync(self):
        data = {'nama': self.identity, 'skor': self.score, 'id_sesi': self.TOKEN_CLOUD, 'tanggal_waktu': time.strftime('%Y-%m-%d %H:%M:%S')}
        supabase.table("skor").insert(data).execute()
        self.btn_sync.setEnabled(False); self.load_ld()

    def load_ld(self):
        res = supabase.table("skor").select("nama,skor").eq("id_sesi", self.TOKEN_CLOUD).order("skor", desc=True).limit(5).execute()
        self.tab.setRowCount(len(res.data))
        for i, r in enumerate(res.data):
            self.tab.setItem(i,0, QTableWidgetItem(str(i+1))); self.tab.setItem(i,1, QTableWidgetItem(r['nama'])); self.tab.setItem(i,2, QTableWidgetItem(str(r['skor'])))

def get_cloud_config():
    try:
        r = supabase.table("settings").select("*").eq("id", 1).single().execute()
        return r.data.get('id_sesi_aktif', '113'), r.data.get('template_aktif', 'dark_teal.xml'), r.data.get('nama_aplikasi', 'IKPA Quiz')
    except: return "113", "dark_teal.xml", "IKPA Quiz"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    TOKEN, THEME, TITLE = get_cloud_config()
    apply_stylesheet(app, theme=THEME)
    win = ClientQuizApp(TOKEN, TITLE); win.show()
    sys.exit(app.exec())