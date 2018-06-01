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

def search(arr, min_ele, max_ele):
	for i in range(0, len(arr)):
		if arr[i] >= min_ele and arr[i] <= max_ele :
			return True
	return False