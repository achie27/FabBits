"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Where it all starts!
	Last updated - 11/05/2018

"""

import os, sys
import threading
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

		self.processors = {
			"MOVIES" : [self.jokes_detector],
			"SPORTS" : []
		}

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
		self.current_use_case = self.sender().currentItem().id
		# TODO - popup window for use cases that need extra info


	def find_fabbits(self):
		thread = MyThread("1", self)
		thread.start()


	def jokes_detector(self):
		print("processing")
		jokes = LaughDetector(self.file)
		jokes.find_laughs()
		self.fabbit = jokes.get_laughs()
		print("done processing fabbits for "+self.file)


	def save_fabbits(self):
		self.fabbit['bits'].write_videofile("[FabBits] "+self.filename, codec='libx264')


	def set_file(self):
		self.file = QFileDialog.getOpenFileName(
			self, 'Open file', '/home'
		)

		if self.file[0]:
			self.file = self.file[0]

		self.filename = self.file[ self.file.rfind('/')+1 : ]
		print("loaded "+ self.file)


class MyThread(threading.Thread):
	def __init__(self, name, qt_object):
		super().__init__()
		print("initialising thread")

		self.name = name
		self.cat = qt_object.current_cat
		self.qt_object = qt_object
		self.use_case = qt_object.current_use_case

	def run(self):
		print("running thread")
		self.qt_object.processors[self.cat][self.use_case]()		
		print("exiting thread")


app = QApplication(sys.argv)
win = Main()
sys.exit(app.exec_())