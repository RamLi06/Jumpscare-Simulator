import sys
import random
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QMovie
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# --- CONSTANTES DE COMPATIBILIDADE ---
# Mantidas para não quebrar o __init__.py
GIF_PATH = 'assets/video_jumpscare/Withered_Chica.gif'
SOUND_PATH = 'assets/audios/jumpscare_fnaf2.wav'

class JumpscareController:
    def __init__(self, gif_path, sound_path, probability, interval_seconds):
        self.gif_path = gif_path
        self.sound_path = sound_path
        self.probability = probability
        self.interval_seconds = interval_seconds
        
        self.scare_window = QMainWindow()
        
        # --- AJUSTE 1: TRANSPARÊNCIA ---
        # Removemos o styleSheet preto
        # Adicionamos a flag WA_TranslucentBackground
        self.scare_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.scare_window.setAttribute(Qt.WA_TranslucentBackground) 
        
        # Configurar GIF
        self.label = QLabel(self.scare_window)
        
        # Verifica caminhos para evitar erro
        current_gif = self.gif_path
        if not os.path.exists(current_gif) and os.path.exists(GIF_PATH):
             current_gif = GIF_PATH
             
        self.movie = QMovie(current_gif)
        # O label também precisa ser transparente
        self.label.setStyleSheet("background-color: transparent;")
        self.label.setMovie(self.movie)
        self.label.setScaledContents(True)
        self.scare_window.setCentralWidget(self.label)

        # Configurar Som
        self.player = QMediaPlayer()
        
        audio_file = self.sound_path if (self.sound_path and self.sound_path != "none") else None
        
        if audio_file:
            abs_path = os.path.abspath(audio_file)
            if os.path.exists(abs_path):
                url = QUrl.fromLocalFile(abs_path)
                content = QMediaContent(url)
                self.player.setMedia(content)
                self.player.setVolume(100)

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_probability)

    def start(self):
        ms = int(self.interval_seconds * 1000)
        self.check_timer.start(ms)
        print(f"[MONITOR] Rodando... Chance: {self.probability} a cada {self.interval_seconds}s")

    def check_probability(self):
        """Roda periodicamente."""
        if random.random() < self.probability:
            self.trigger_jumpscare()

    def trigger_jumpscare(self):
        print("[!!!] SUSTO ACIONADO!")
        
        # 1. PAUSA a checagem para não encavalar sustos
        self.check_timer.stop()
        
        # 2. Mostra a janela (agora transparente)
        self.scare_window.showFullScreen()
        
        if self.movie.isValid():
            self.movie.start()
        
        self.player.play()
        
        # 3. Define quanto tempo o susto dura (ex: 2.5 segundos)
        QTimer.singleShot(900, self.finish_scare)

    def finish_scare(self):
        """Finaliza o susto mas MANTÉM o programa rodando."""
        print("[ALIVIO] Susto acabou. Retomando vigilância...")
        
        # Para o som e o gif
        self.movie.stop()
        self.player.stop()
        
        # Esconde a janela (não fecha o app)
        self.scare_window.hide()
        
        # --- AJUSTE 2: CONTINUIDADE ---
        # Reinicia o timer para continuar testando a sorte
        ms = int(self.interval_seconds * 1000)
        self.check_timer.start(ms)

# --- ALIAS DE COMPATIBILIDADE ---
JumpscareGIF = JumpscareController 

def run_continuous(gif_path=GIF_PATH, sound_path=SOUND_PATH, probability=0.01, interval_seconds=1.0):
    """Função chamada pelo main.py"""
    # Verifica se já existe uma instância do QApplication (caso o main já tenha criado)
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    controller = JumpscareController(
        gif_path, 
        sound_path, 
        probability=probability, 
        interval_seconds=interval_seconds
    )
    controller.start()
    
    # Executa o loop de eventos. Como não chamamos quit() no finish_scare,
    # ele vai ficar rodando para sempre até você fechar o processo manualmente.
    sys.exit(app.exec_())