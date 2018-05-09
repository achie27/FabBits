"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Where it all starts!
	Last updated - 08/05/2018

"""

import os, sys
from PyQt5.QtWidgets import \
	QApplication, QMainWindow, QPushButton, QWidget, QListWidget,\
	QListWidgetItem, QFileDialog, QLabel
from PyQt5 import QtCore

from laugh_detector import LaughDetector
import helpers

class Main(QWidget):
	def __init__(self):
		super().__init__()

		self.current_cat = ""
		self.categories = ["MOVIES", "SPORTS"]

		self.use_cases = {}
		self.use_cases['MOVIES'] = [
			"Jokes from sitcoms", "Action sequences",
			"Different settings", "Actor specific scenes"
		]

		self.use_cases['SPORTS'] = [
			"Goals in soccer", "Three-pointers in basketball",
			"Slow-mos", "Goal misses in soccer"
		]
		self.current_use_case = ""

		self.fabbit = {}

		self.width, self.height = 750, 475
		self.create_gui()


	def create_gui(self):

		total_cats = len(self.categories)
		btn_height, btn_width = 70, self.width/total_cats
		self.btns = [0]*total_cats
		
		for i in range(0, total_cats):
			self.btns[i] = QPushButton(self.categories[i], self)
			self.btns[i].clicked.connect(self.update_list)
			self.btns[i].setGeometry(
				i*btn_width, 0, btn_width, btn_height
			) 

		list_width, list_height = 200, 300
		self.list = QListWidget(self)
		self.list.clicked.connect(self.process_use_case)
		self.list.setGeometry(0, btn_height, list_width, list_height)

		self.file_btn = QPushButton("Choose file", self)
		self.file_btn.clicked.connect(self.set_file)
		self.file_btn.setGeometry(
			0, list_height+btn_height, 
			list_width, self.height - (list_height+btn_height)
		)

		op_btn_height = (self.height - (list_height+btn_height))/2
		op_btn_width = list_width*3/4

		btn = QPushButton("Find FabBits", self)
		btn.clicked.connect(self.find_fabbits)
		btn.setGeometry(
			self.width-list_width*3/4, list_height+btn_height, 
			op_btn_width, op_btn_height
		)

		btn = QPushButton("Save FabBits", self)
		btn.clicked.connect(self.save_fabbits)
		btn.setGeometry(
			self.width-list_width*3/4, 
			list_height+btn_height+op_btn_height, 
			op_btn_width, op_btn_height
		)

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
			self.width - list_width, self.height-btn_height-op_btn_height			
		)

		self.setWindowTitle('FabBits')
		self.setFixedSize(self.width, self.height)

		self.show()


	def update_list(self, btn):
		self.list.clear()
		self.current_cat, id = self.sender().text(), 0
		for use_case in self.use_cases[self.current_cat]:
			obj = QListWidgetItem(use_case, self.list)
			obj.id = id
			id+=1


	def process_use_case(self):
		self.current_use_case = self.sender().currentItem().id
		# popup window for use cases that need extra info

	def find_fabbits(self):

		# will make this better soon
		if self.current_cat == "MOVIES":
			if self.current_use_case == 0:
				jokes = LaughDetector(self.file)
				jokes.find_laughs()
				self.fabbit = jokes.get_laughs()

		print("finding done")


	def save_fabbits(self):
		self.fabbit['bits'].write_videofile("FabBits.mp4", codec='libx264')


	def set_file(self):
		self.file = QFileDialog.getOpenFileName(
			self, 'Open file', '/home'
		)

		if self.file[0]:
			self.file = self.file[0]

		print(self.file)



app = QApplication(sys.argv)
win = Main()
sys.exit(app.exec_())