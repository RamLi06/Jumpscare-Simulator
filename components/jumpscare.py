import sys
import random
from pathlib import Path
import traceback
from PyQt6.QtCore import Qt, QUrl, QSize, QTimer, QObject
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtMultimedia import QSoundEffect

import os

GIF_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Mangle.gif')
SOUND_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'jumpscare_fnaf2.wav')  # Exemplo


class JumpscareGIF(QWidget):
    def __init__(self, gif_path: str, sound_path: str = None, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput  # Remove se quiser poder clicar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # GIF animado
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Verificar se o GIF existe
        if not Path(gif_path).exists():
            print(f"[ERRO] GIF não encontrado: {gif_path}")
            print(f"[INFO] Caminho absoluto esperado: {Path(gif_path).resolve()}")
            raise FileNotFoundError(f"GIF não encontrado: {gif_path}")
        
        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print(f"[ERRO] QMovie não conseguiu carregar o GIF: {gif_path}")
            raise ValueError(f"GIF inválido: {gif_path}")
        
        self.label.setMovie(self.movie)

        layout.addWidget(self.label)
        self.setLayout(layout)

        # Som sincronizado
        self.sound = None
        self.last_frame = -1  # Rastrear frame anterior para detectar loop
        
        if sound_path and Path(sound_path).exists():
            try:
                self.sound = QSoundEffect()
                sound_url = QUrl.fromLocalFile(str(Path(sound_path).resolve()))
                self.sound.setSource(sound_url)
                self.sound.setVolume(1.0)
                
                # Aguardar o som carregar
                if self.sound.status() == QSoundEffect.Status.Loading:
                    print("[INFO] Aguardando som carregar...")
                
                # Log detalhado
                print(f"[INFO] Som configurado: {sound_path}")
                print(f"[INFO] URL do som: {sound_url.toString()}")
                print(f"[INFO] Status do som: {self.sound.status()}")
                print(f"[INFO] Som está carregado: {self.sound.isLoaded()}")
                
            except Exception as e:
                print(f"[AVISO] Erro ao carregar som: {e}")
                self.sound = None
        elif sound_path:
            print(f"[AVISO] Arquivo de som não encontrado: {sound_path}")
            print(f"[INFO] Caminho absoluto esperado: {Path(sound_path).resolve()}")
        else:
            print("[INFO] Nenhum som configurado (sound_path é None)")

        # Conectar frame changed para tocar som a cada loop
        self.movie.frameChanged.connect(self.sync_sound)

    def sync_sound(self, frame):
        """Tocar som toda vez que o GIF reiniciar (voltar ao frame 0)."""
        if not self.sound:
            return
        
        # Detectar quando o GIF volta ao início (loop)
        if frame == 0 or (self.last_frame > frame):
            try:
                print(f"[INFO] Loop detectado! Frame atual: {frame}, Frame anterior: {self.last_frame}")
                
                if self.sound.isLoaded():
                    # Parar o som anterior se ainda estiver tocando
                    if self.sound.isPlaying():
                        self.sound.stop()
                    
                    self.sound.play()
                    print("[INFO] Som tocado!")
                else:
                    print("[AVISO] Som ainda não está carregado")
                    
            except Exception as e:
                print(f"[ERRO] Falha ao tocar som: {e}")
        
        self.last_frame = frame

    def show_at_position(self, position: str = "center", allow_upscale: bool = False, margin: int = 0, offset_x: int = 0, offset_y: int = 0, overflow_top: int = 0):
        """Mostra o GIF em uma posição específica da tela.
        
        Args:
            position: Posição desejada. Opções:
                - "center" (padrão): centro da tela
                - "top-left": canto superior esquerdo
                - "top-right": canto superior direito
                - "bottom-left": canto inferior esquerdo
                - "bottom-right": canto inferior direito
                - "top": centro superior
                - "bottom": centro inferior
                - "left": centro esquerdo
                - "right": centro direito
            allow_upscale: Permite ampliar o GIF além do tamanho original
            margin: Margem em pixels das bordas da tela
            offset_x: Deslocamento horizontal adicional em pixels (positivo = direita)
            offset_y: Deslocamento vertical adicional em pixels (positivo = baixo)
            overflow_top: Quantos pixels do GIF ficarão FORA da tela no topo (para efeito de susto vindo de cima)
        """
        # Iniciar o movie ANTES de obter dimensões
        if self.movie.state() != QMovie.MovieState.Running:
            self.movie.start()
        
        # Aguardar um frame para garantir que o tamanho está disponível
        QApplication.processEvents()
        
        screen = QApplication.primaryScreen()
        if not screen:
            print("[ERRO] Não foi possível obter a tela primária")
            self.show()
            return
        
        # Usar geometry() em vez de availableGeometry() para pegar a tela INTEIRA
        geo = screen.geometry()  # Tela completa, incluindo barras
        max_w = max(1, geo.width() - margin * 2)
        max_h = max(1, geo.height() - margin * 2)

        # Obter tamanho do frame atual
        current_pixmap = self.movie.currentPixmap()
        if current_pixmap.isNull():
            print("[AVISO] Pixmap do GIF está nulo, usando tamanho padrão")
            w, h = 400, 400
        else:
            w = current_pixmap.width()
            h = current_pixmap.height()

        if w <= 0 or h <= 0:
            print("[AVISO] Dimensões inválidas do GIF, usando padrão")
            w, h = 400, 400

        # Calcular escala preservando proporção
        scale_w = max_w / w
        scale_h = max_h / h
        scale = min(scale_w, scale_h)

        if not allow_upscale and scale > 1.0:
            scale = 1.0

        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))

        # Aplicar escala ao QMovie
        self.movie.setScaledSize(QSize(new_w, new_h))

        # Calcular posição baseada na escolha
        position = position.lower()
        
        if position == "center":
            x = geo.x() + (geo.width() - new_w) // 2
            y = geo.y() + (geo.height() - new_h) // 2
        elif position == "top-left":
            x = geo.x() + margin
            y = geo.y() + margin
        elif position == "top-right":
            x = geo.x() + geo.width() - new_w - margin
            y = geo.y() + margin
        elif position == "bottom-left":
            x = geo.x() + margin
            y = geo.y() + geo.height() - new_h - margin
        elif position == "bottom-right":
            x = geo.x() + geo.width() - new_w - margin
            y = geo.y() + geo.height() - new_h - margin
        elif position == "top":
            x = geo.x() + (geo.width() - new_w) // 2
            y = geo.y() + margin
        elif position == "bottom":
            x = geo.x() + (geo.width() - new_w) // 2
            y = geo.y() + geo.height() - new_h - margin
        elif position == "left":
            x = geo.x() + margin
            y = geo.y() + (geo.height() - new_h) // 2
        elif position == "right":
            x = geo.x() + geo.width() - new_w - margin
            y = geo.y() + (geo.height() - new_h) // 2
        else:
            print(f"[AVISO] Posição '{position}' inválida, usando 'center'")
            x = geo.x() + (geo.width() - new_w) // 2
            y = geo.y() + (geo.height() - new_h) // 2

        # Aplicar offsets personalizados
        x += offset_x
        y += offset_y
        
        # Aplicar overflow do topo (mover o GIF para CIMA, saindo da tela)
        y -= overflow_top

        self.setGeometry(x, y, new_w, new_h)
        
        # IMPORTANTE: Para garantir que fique no topo absoluto
        self.showFullScreen() if position in ["top", "top-left", "top-right"] and margin == 0 else self.show()
        self.raise_()
        self.activateWindow()
        
        # Força a posição exata após mostrar
        self.move(x, y)
        
        # FORÇAR TOCAR SOM IMEDIATAMENTE na primeira exibição
        if self.sound:
            QTimer.singleShot(50, self._force_play_sound)
        
        print(f"[INFO] Janela exibida em ({x}, {y}) com tamanho {new_w}x{new_h}, overflow_top={overflow_top}")
    
    def _force_play_sound(self):
        """Força o som a tocar na primeira vez (método backup)."""
        if self.sound:
            try:
                if self.sound.isLoaded():
                    print("[INFO] Forçando reprodução inicial do som...")
                    self.sound.play()
                else:
                    print("[AVISO] Som ainda não carregado, tentando novamente...")
                    QTimer.singleShot(100, self._force_play_sound)
            except Exception as e:
                print(f"[ERRO] Falha ao forçar som: {e}")

    def show_centered(self, allow_upscale: bool = False, margin: int = 0):
        """Atalho para mostrar centralizado (mantém compatibilidade)."""
        self.show_at_position("center", allow_upscale, margin)

    def mousePressEvent(self, event):
        """Fechar ao clicar."""
        print("[INFO] Janela fechada por clique")
        self.close()

    def keyPressEvent(self, event):
        """Fechar com ESC."""
        if event.key() == Qt.Key.Key_Escape:
            print("[INFO] Janela fechada por ESC")
            self.close()


def run_app(gif_path: str = GIF_PATH, sound_path: str = SOUND_PATH, *, probability: float = 0.01):
    """Roda o aplicativo com uma chance probabilística de exibir o jumpscare."""
    if not (0.0 <= probability <= 1.0):
        raise ValueError("probability must be between 0.0 and 1.0")

    roll = random.random()
    print(f"[INFO] Roll: {roll:.4f}, Probabilidade: {probability}")
    
    if roll >= probability:
        print(f"[INFO] Jumpscare não disparado (roll={roll:.4f} >= probability={probability})")
        return 0

    print("[INFO] Jumpscare disparado!")
    
    # Disparou: inicializa a GUI
    try:
        app = QApplication(sys.argv)
        
        # Usar sound_path apenas se não for None ou string vazia
        actual_sound = sound_path if sound_path and sound_path != "none" else None
        
        win = JumpscareGIF(gif_path, actual_sound)
        
        # Para susto vindo de cima (metade do GIF fica fora da tela):
        win.show_at_position("center", overflow_top=300)  # Ajuste o valor conforme necessário
        
        # Outras opções:
        # win.show_centered()  # Centro normal
        # win.show_at_position("top", overflow_top=500)  # Muito do GIF fora da tela
        # win.show_at_position("center", offset_y=-200)  # Alternativa usando offset
        
        return app.exec()
    except Exception as exc:
        print("[ERRO] Exceção ao executar jumpscare:")
        traceback.print_exc()
        return 1


class JumpscareController(QObject):
    """Controlador que verifica periodicamente a probabilidade e exibe o jumpscare."""

    def __init__(self, gif_path: str, sound_path: str = None, probability: float = 0.01, interval_seconds: float = 1.0):
        super().__init__()
        self.gif_path = gif_path
        self.sound_path = sound_path if sound_path and sound_path != "none" else None
        self.probability = float(probability)
        self.interval_ms = max(100, int(interval_seconds * 1000))
        self._showing = False
        self._current_window = None

        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self._on_timeout)

    def start(self):
        """Inicia o timer de verificação."""
        print(f"[INFO] Controller iniciado (probabilidade={self.probability}, intervalo={self.interval_ms}ms)")
        self.timer.start()

    def stop(self):
        """Para o timer de verificação."""
        print("[INFO] Controller parado")
        self.timer.stop()

    def _on_timeout(self):
        """Callback executado a cada intervalo."""
        if self._showing:
            return
        
        try:
            roll = random.random()
            if roll < self.probability:
                print(f"[INFO] Jumpscare disparado! (roll={roll:.4f} < {self.probability})")
                self._showing = True
                self._current_window = JumpscareGIF(self.gif_path, self.sound_path)
                self._current_window.destroyed.connect(self._on_window_closed)
                
                # Para susto vindo de cima:
                self._current_window.show_at_position("center", overflow_top=300)
                # ou: self._current_window.show_centered()  # Centro normal
        except Exception:
            print("[ERRO] Exceção no timeout handler:")
            traceback.print_exc()

    def _on_window_closed(self, *args, **kwargs):
        """Callback quando a janela é fechada."""
        print("[INFO] Janela de jumpscare fechada")
        self._showing = False
        self._current_window = None


def run_continuous(gif_path: str = GIF_PATH, sound_path: str = SOUND_PATH, *, probability: float = 0.01, interval_seconds: float = 1.0):
    """Roda um loop contínuo que testa a probabilidade periodicamente."""
    if not (0.0 <= probability <= 1.0):
        raise ValueError("probability must be between 0.0 and 1.0")

    try:
        app = QApplication(sys.argv)
        
        actual_sound = sound_path if sound_path and sound_path != "none" else None
        
        controller = JumpscareController(
            gif_path, 
            actual_sound, 
            probability=probability, 
            interval_seconds=interval_seconds
        )
        controller.start()
        
        print("[INFO] Aplicação em modo contínuo iniciada. Pressione Ctrl+C para sair.")
        return app.exec()
    except Exception:
        print("[ERRO] Exceção ao executar controller contínuo:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Para testar, use probabilidade alta
    # sys.exit(run_app(probability=1.0))  # 100% de chance
    
    # Modo normal (1% de chance)
    sys.exit(run_app())
    
    # Modo contínuo (verifica a cada segundo)
    # sys.exit(run_continuous(probability=0.01, interval_seconds=1.0))