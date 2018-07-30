"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Where it all starts!
	Last updated - 13/06/2018

"""

import os, sys
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import \
	QApplication, QMainWindow, QPushButton, QWidget, QListWidget,\
	QListWidgetItem, QFileDialog, QLabel, QSlider, QStyle, QPlainTextEdit

from laugh_detector import LaughDetector
from shot_detector import DetectShots
from action_scene_detector import DetectAction
from goal_detector import DetectGoal
from helpers import HelperThread

class Main(QWidget):
	def __init__(self):
		super().__init__()

		self.current_cat = ""
		self.categories = ["MOVIES", "SPORTS"]

		self.use_cases = {}
		self.use_cases['MOVIES'] = [
			"Jokes from sitcoms", "Action sequences",
			"Summary", "Actor specific scenes"
		]

		self.use_cases['SPORTS'] = [
			"Goals in soccer", "Three-pointers in basketball",
			"Slow-mos", "Goal misses in soccer"
		]
		self.current_use_case = ""

		# methods that should be called for
		# finding each use case
		self.processors = {
			"MOVIES" : [
				self.jokes_detector, 
				self.action_detector, 
				self.shot_detector,
				0
			],
			"SPORTS" : [
				self.goal_detector,
				0,
				0,
				0
			]
		}

		# the object of current use-case's class
		self.fabbit = 0

		self.width, self.height = 750, 475
		self.create_gui()


	def create_gui(self):
		"""
		Yep, creates the GUI.

		"""

		total_cats = len(self.categories)
		btn_height, btn_width = 70, self.width/total_cats
		self.btns = [0]*total_cats
		
		# add the category - movies and sports - buttons
		for i in range(0, total_cats):
			self.btns[i] = QPushButton(self.categories[i], self)
			self.btns[i].clicked.connect(self.update_list)
			self.btns[i].setGeometry(
				i*btn_width, 0, btn_width, btn_height
			) 

		# add the side bar that containes use-cases
		list_width, list_height = 200, 300
		self.list = QListWidget(self)
		self.list.clicked.connect(self.process_use_case)
		self.list.setGeometry(0, btn_height, list_width, list_height)

		# add more buttons
		self.file_btn = QPushButton("Choose file", self)
		self.file_btn.clicked.connect(self.set_file)
		self.file_btn.setGeometry(
			0, list_height+btn_height, 
			list_width, self.height - (list_height+btn_height)
		)

		op_btn_height = (self.height - (list_height+btn_height))/2
		op_btn_width = list_width*3/4

		op_btn1 = QPushButton("Find FabBits", self)
		op_btn1.clicked.connect(self.find_fabbits)
		op_btn1.setGeometry(
			self.width-list_width*3/4, list_height+btn_height, 
			op_btn_width, op_btn_height
		)

		op_btn2 = QPushButton("Save FabBits", self)
		op_btn2.clicked.connect(self.save_fabbits)
		op_btn2.setGeometry(
			self.width-list_width*3/4, 
			list_height+btn_height+op_btn_height, 
			op_btn_width, op_btn_height
		)

		self.status_bar = QPlainTextEdit(self)
		self.status_bar.setReadOnly(True)
		self.status_bar.setGeometry(
			list_width, list_height+btn_height,
			self.width - list_width - op_btn_width, 2*op_btn_height			
		)


		class StatusStream():
			def __init__(self, textbox):
				self.textbox = textbox

			def write(self, text):
				self.textbox.appendPlainText(text)

			def flush(self):
				self.textbox.clear()

		sys.stdout = StatusStream(self.status_bar)


		play_button_h, play_button_w = 30, 30

		vw = QVideoWidget(self)
		vw.setGeometry(
			list_width, btn_height,
			self.width - list_width, 
			self.height-btn_height-2*op_btn_height-play_button_h			
		)
		
		self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
		self.media_player.setVideoOutput(vw)
		self.media_player.stateChanged.connect(self.state_change)
		self.media_player.positionChanged.connect(self.set_pos_player)
		self.media_player.durationChanged.connect(self.set_duration)

		self.vid_button = QPushButton(self)
		self.vid_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
		self.vid_button.clicked.connect(self.play_vid)
		self.vid_button.setEnabled(False)
		self.vid_button.setGeometry(
			list_width, self.height-2*op_btn_height-play_button_h,
			play_button_w, play_button_h
		)

		self.vid_slider = QSlider(QtCore.Qt.Horizontal, self)
		self.vid_slider.sliderMoved.connect(self.set_pos_slider)
		self.vid_slider.setGeometry(
			list_width+play_button_w, self.height-2*op_btn_height-play_button_h,
			self.width+list_width-play_button_w, play_button_h
		)			


		self.update_list("MOVIES")
		self.setWindowTitle('FabBits')
		self.setFixedSize(self.width, self.height)

		self.show()


	def state_change(self, state):
		"""


		"""

		if self.media_player.state() == QMediaPlayer.PlayingState:
			self.vid_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
		else:
			self.vid_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


	def play_vid(self):
		"""


		"""
		if self.media_player.state() == QMediaPlayer.PlayingState:
			self.media_player.pause()
		else:
			self.media_player.play()


	def set_pos_slider(self, pos):
		"""


		"""
		self.media_player.setPosition(pos)



	def set_pos_player(self, pos):
		"""


		"""
		self.vid_slider.setValue(pos)



	def set_duration(self, dur):
		"""


		"""
		self.vid_slider.setRange(0, dur)


	def update_list(self, cat):
		"""
		Sets the chosen category and updates the corresponding
		use-cases in the side bar.

		"""

		self.list.clear()

		if cat :
			self.current_cat = cat
		else :
			self.current_cat = self.sender().text()
			
		id = 0
		for use_case in self.use_cases[self.current_cat]:
			obj = QListWidgetItem(use_case, self.list)
			obj.id = id
			id+=1

	def process_use_case(self):
		"""
		Sets the chosen use-case and acts as an intermediary

		"""

		self.current_use_case = self.sender().currentItem().id

		# TODO - popup window for use cases that need extra info
		#		like actor specific scenes to ask for actor name
		pass


	def find_fabbits(self):
		"""
		Finds the use-case.

		"""
		cat = self.current_cat
		use_case = self.current_use_case
		f = lambda : self.processors[cat][use_case]()
		thread = HelperThread("Finding FabBit 1", f)
		thread.start()


	def jokes_detector(self):
		print("processing")
		jokes = LaughDetector(self.file)
		jokes.process()
		self.fabbit = jokes
		print("done processing fabbits for "+self.file)


	def shot_detector(self):
		print("processing")
		summary = DetectShots(self.file)
		summary.process()
		self.fabbit = summary
		print("done processing fabbits for "+self.file)


	def action_detector(self):
		print("processing")
		action = DetectAction(self.file)
		action.process()
		self.fabbit = action
		print("done processing fabbits for "+self.file)


	def goal_detector(self):
		print("processing")
		goals = DetectGoal(self.file)
		goals.process()
		self.fabbit = goals
		print("done processing fabbits for "+self.file)


	def save_fabbits(self):
		thread = HelperThread("Saving 1", self.fabbit.save)
		thread.start()


	def set_file(self):
		"""
		For file dialog to get input video

		"""

		self.file = QFileDialog.getOpenFileName(
			self, 'Open file', '/home'
		)

		if self.file[0]:
			self.file = self.file[0]

		self.media_player.setMedia(
			QMediaContent(QtCore.QUrl.fromLocalFile(self.file))
		)
		self.vid_button.setEnabled(True)

		self.filename = self.file[ self.file.rfind('/')+1 : ]
		print("loaded "+ self.filename)


if __name__ == '__main__':

	app = QApplication(sys.argv)
	win = Main()
	sys.exit(app.exec_())