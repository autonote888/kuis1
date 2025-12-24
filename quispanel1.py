import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from supabase import create_client, Client
from qt_material import apply_stylesheet

# Konfigurasi Supabase
URL = "https://bxlfaofmraznomebbrlh.supabase.co"
KEY = "sb_publishable_KuRg1y2stBUHfJshbCUpbg_dvD8s329"
supabase: Client = create_client(URL, KEY)

class MasterAdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IKPA - Master Admin Dashboard")
        self.setFixedSize(500, 750)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(30, 30, 30, 30)
        
        self.show_login()

    def apply_ui_style(self, widget):
        widget.setStyleSheet("""
            QLabel { color: #FFFFFF; font-weight: bold; }
            QLineEdit { background-color: #121212; color: #00FFCC; border: 2px solid #333333; padding: 10px; border-radius: 8px; }
            QComboBox { background-color: #121212; color: #FFFFFF; border: 2px solid #333333; padding: 10px; border-radius: 8px; }
        """)

    def create_card(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e1e; border-radius: 20px; border: 1px solid #333333;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30); shadow.setYOffset(10); shadow.setColor(QColor(0, 0, 0, 200))
        frame.setGraphicsEffect(shadow)
        return frame

    def show_login(self):
        self.clear_layout()
        self.layout.addStretch()
        card = self.create_card()
        lay = QVBoxLayout(card); lay.setContentsMargins(30,40,30,40)
        
        header = QLabel("🔐 ADMIN ACCESS")
        header.setStyleSheet("font-size: 22px; color: #00bcd4; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignCenter); lay.addWidget(header)
        
        self.input_pass = QLineEdit(); self.input_pass.setPlaceholderText("Password")
        self.input_pass.setEchoMode(QLineEdit.Password); self.input_pass.setFixedHeight(50)
        lay.addWidget(self.input_pass)

        btn = QPushButton("LOGIN SYSTEM"); btn.setFixedHeight(55)
        btn.clicked.connect(self.check_login); lay.addWidget(btn)
        
        self.apply_ui_style(card)
        self.layout.addWidget(card); self.layout.addStretch()

    def check_login(self):
        if self.input_pass.text() == "admin123": self.show_dashboard()
        else: QMessageBox.critical(self, "Error", "Password Salah!")

    def show_dashboard(self):
        self.clear_layout()
        header = QLabel("⚙️ GLOBAL CONTROL")
        header.setStyleSheet("font-size: 24px; color: #ffb300; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter); self.layout.addWidget(header)

        card = self.create_card(); lay = QVBoxLayout(card); lay.setContentsMargins(25,25,25,25); lay.setSpacing(15)

        lay.addWidget(QLabel("ACTIVE SESSION ID (TOKEN)"))
        self.edit_token = QLineEdit(); self.edit_token.setFixedHeight(45); lay.addWidget(self.edit_token)

        lay.addWidget(QLabel("CLIENT APP TITLE"))
        self.edit_title = QLineEdit(); self.edit_title.setFixedHeight(45); lay.addWidget(self.edit_title)

        lay.addWidget(QLabel("VISUAL FRAMEWORK THEME"))
        self.combo_theme = QComboBox(); self.combo_theme.setFixedHeight(45)
        self.combo_theme.addItems(['dark_teal.xml', 'dark_amber.xml', 'dark_purple.xml', 'light_blue.xml', 'dark_cyan.xml'])
        lay.addWidget(self.combo_theme)

        self.apply_ui_style(card)
        self.layout.addWidget(card); self.layout.addSpacing(20)

        self.btn_update = QPushButton("🚀 DEPLOY TO CLOUD"); self.btn_update.setFixedHeight(65)
        self.btn_update.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 16px; border-radius: 12px;")
        self.btn_update.clicked.connect(self.push_settings); self.layout.addWidget(self.btn_update)
        
        self.fetch_settings()

    def fetch_settings(self):
        try:
            res = supabase.table("settings").select("*").eq("id", 1).single().execute()
            if res.data:
                self.edit_token.setText(res.data.get('id_sesi_aktif', ''))
                self.edit_title.setText(res.data.get('nama_aplikasi', ''))
                self.combo_theme.setCurrentText(res.data.get('template_aktif', 'dark_teal.xml'))
        except: pass

    def push_settings(self):
        try:
            supabase.table("settings").update({
                "id_sesi_aktif": self.edit_token.text(),
                "nama_aplikasi": self.edit_title.text(),
                "template_aktif": self.combo_theme.currentText()
            }).eq("id", 1).execute()
            QMessageBox.information(self, "Success", "Konfigurasi Berhasil Di-Deploy!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Update Gagal: {e}")

    def clear_layout(self):
        for i in reversed(range(self.layout.count())): 
            w = self.layout.itemAt(i).widget()
            if w: w.setParent(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MasterAdminPanel(); window.show()
    sys.exit(app.exec())