"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Where it all starts!
	Last updated - 13/06/2018

"""

import os, sys
from PyQt5.QtWidgets import \
	QApplication, QMainWindow, QPushButton, QWidget, QListWidget,\
	QListWidgetItem, QFileDialog, QLabel
from PyQt5 import QtCore

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

		#placeholders for now
		placeholder1 = QLabel("Status bar here soon!", self)
		placeholder1.setAlignment(QtCore.Qt.AlignCenter)
		placeholder1.setGeometry(
			list_width, list_height+btn_height,
			self.width - list_width - op_btn_width, 2*op_btn_height			
		)
		
		placeholder2 = QLabel("Video player here soon!", self)
		placeholder2.setAlignment(QtCore.Qt.AlignCenter)
		placeholder2.setGeometry(
			list_width, btn_height,
			self.width - list_width, 
			self.height-btn_height-2*op_btn_height			
		)


		self.update_list("MOVIES")
		self.setWindowTitle('FabBits')
		self.setFixedSize(self.width, self.height)

		self.show()


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

		self.filename = self.file[ self.file.rfind('/')+1 : ]
		print("loaded "+ self.filename)


if __name__ == '__main__':

	app = QApplication(sys.argv)
	win = Main()
	sys.exit(app.exec_())