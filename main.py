
import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia
from PyQt5.QtMultimedia import QSoundEffect
from ui_untitled import Ui_JumpscareSim


GIF_MENU = 'assets/FNAF_static.gif'  # Coloque seu GIF de menu aqui
MUSIC_MENU = 'assets/audios/menu.wav'  # Coloque sua música de menu aqui

SUSTOS = {
	'Chica': {
		'gif': os.path.join('assets/video_jumpscare', 'Withered_Chica.gif'),
		'sound': os.path.join('assets/audios', 'jumpscare_fnaf2.wav')
	},
	'rat': {
		'gif': os.path.join('assets/video_jumpscare', 'Monster_Rat.gif'),
		'sound': os.path.join('assets/audios', 'rat_sound.wav')
	},
	'Mangle': {
		'gif': os.path.join('assets/video_jumpscare', 'Mangle.gif'),
		'sound': os.path.join('assets/audios', 'jumpscare_fnaf2.wav')
	},
	'Vinnie': {
		'gif': os.path.join('assets/video_jumpscare','Vinnie.gif'),
		'sound': os.path.join('assets/audios', 'Vinnie.wav')
	}
}


class MainWindow(QtWidgets.QMainWindow, Ui_JumpscareSim):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		# Tamanho fixo da janela (igual ao do .ui)
		self.setFixedSize(784, 431)

		# Adiciona GIF animado no label
		self.movie = QtGui.QMovie(GIF_MENU)
		self.label.setMovie(self.movie)
		self.movie.start()

		# Música de fundo
		self.player = QtMultimedia.QMediaPlayer()
		url = QtCore.QUrl.fromLocalFile(os.path.abspath(MUSIC_MENU))
		self.player.setMedia(QtMultimedia.QMediaContent(url))
		self.player.setVolume(50)
		self.player.play()

		# Conecta botões
		self.pushButton.clicked.connect(lambda: self.start_jumpscare('Chica'))
		self.pushButton_2.clicked.connect(lambda: self.start_jumpscare('rat'))
		self.pushButton_3.clicked.connect(lambda: self.start_jumpscare('Mangle'))
		self.pushButton_5.clicked.connect(lambda: self.start_jumpscare('Vinnie'))
		# self.pushButton_2.clicked.connect(lambda: self.start_jumpscare('foxy'))

		self.select_sound = QSoundEffect()
		self.select_sound.setSource(QtCore.QUrl.fromLocalFile(os.path.abspath('assets/audios/select.wav')))
		self.select_sound.setVolume(0.5)

		for btn in [self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4, self.pushButton_5, self.pushButton_6]:
			btn.installEventFilter(self)


	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.Enter:
			if obj in [self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4, self.pushButton_5, self.pushButton_6]:
				if self.select_sound.isLoaded():
					self.select_sound.play()
		return super().eventFilter(obj, event)

	def start_jumpscare(self, tipo):
		# Para música e fecha menu
		self.player.stop()
		self.close()
		QtWidgets.QApplication.processEvents()
		# Inicia o modo jumpscare em um novo processo
		gif = SUSTOS[tipo]['gif']
		sound = SUSTOS[tipo]['sound']
		# Chama o próprio script com argumentos para modo jumpscare
		args = [sys.executable, sys.argv[0], '--jumpscare', gif, sound]
		subprocess.Popen(args)
		# Encerra o app do menu
		QtWidgets.QApplication.quit()



def main():
	# Se for chamado com --jumpscare, roda só o modo jumpscare
	if len(sys.argv) > 1 and sys.argv[1] == '--jumpscare':
		from components.jumpscare import run_continuous
		gif = sys.argv[2] if len(sys.argv) > 2 else SUSTOS['Chica']['gif']
		sound = sys.argv[3] if len(sys.argv) > 3 else SUSTOS['Chica']['sound']
		run_continuous(gif_path=gif, sound_path=sound, probability=1.0, interval_seconds=1.0)
		return
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
