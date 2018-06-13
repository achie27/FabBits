"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Contains helper classes and functions
	Last updated - 10/05/2018

"""

import threading

class HelperThread(threading.Thread):
	def __init__(self, name, f):
		super().__init__()
		self.name = name
		self.f = f

	def run(self):
		print("Thread "+self.name+" has started.")
		self.f()
		print("Thread "+self.name+" has finished.")

def center(qtobject, parent):
	qr = qtobject.frameGeometry()
	cp = parent.frameGeometry().center()
	qr.moveCenter(cp)
	qtobject.move(qr.topLeft())

def search(arr, min_ele, max_ele):
	for i in range(0, len(arr)):
		if arr[i] >= min_ele and arr[i] <= max_ele :
			return True
	return False