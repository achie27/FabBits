"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Contains helper functions
	Last updated - 01/05/2018

"""

def center(qtobject, parent):
	qr = qtobject.frameGeometry()
	cp = parent.frameGeometry().center()
	qr.moveCenter(cp)
	qtobject.move(qr.topLeft())