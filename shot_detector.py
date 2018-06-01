"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Detects shot boundaries and groups them into scenes
	Last updated - 1/06/2018

	TODO : Make key frame extraction better

"""

import cv2
import numpy as np 
from helpers import search

class DetectShots():
	def __init__(self, file_path):
		self.k, self.N = 5, 320*240
		self.a, self.b, self.s = 0.5, 0.25, 8
		self.hist, self.fd, self.shots, = [], [], []
		self.total_shots, self.total_frames = 0, 0
		self.key_frames, self.out = [], []

		self.file = cv2.VideoCapture(file_path)
		self.filename = file_path[0:file_path.rfind('.')]
		self.fps = self.file.get(cv2.CAP_PROP_FPS)
		self.T = int(self.fps * 300)


	def get_shots(self):
		self.find_frame_difference()
		self.find_shots()

		shots = [i/self.fps for i in self.shots]
		return {
			"timestamps" : shots
		}

	def find_frame_difference(self):
		counter = 0
		while self.file.isOpened():
			suc, fr = self.file.read()
			if not suc : break

			fr = cv2.resize(fr, (320, 240))
			gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
			hist_fr = cv2.calcHist([gray_fr], [0], None, [256], [0, 256])

			if counter >= self.k :
				tmp = np.abs(hist_fr - self.hist[counter-self.k])
				self.fd.append(
					np.sum(tmp)/(2*self.N)
				)

			self.hist.append(hist_fr)
			counter+=1

		self.total_frames = counter - 1


	def find_shots(self):
		counter = 0
		diff_fd = np.diff(self.fd)
		for i in range(2, self.total_frames - self.k):
			local_max=diff_fd[i-1]>diff_fd[i-2] and diff_fd[i-1]>diff_fd[i]
			if self.fd[i] > self.a and local_max :
				if not search(self.shots, int(i-self.fps*8), int(i+self.fps*8)):
					self.shots.append(i - self.k)
			else :
				if self.fd[i] > self.b and self.fd[i-1] > self.b:
					counter += 1
				else:
					counter = 0

				if counter >= self.s :
					counter = 0
					if not search(self.shots, i-self.fps*8, i+self.fps*8):
						self.shots.append(i - self.s - self.k)

		self.total_shots = len(self.shots) 


	def find_key_frames(self):
		if self.total_frames==0 or self.total_shots==0:
			self.find_frame_difference()
			self.find_shots()

		for i in range(0, self.total_shots):
			pre = 0 if i == 0 else self.shots[i-1]
			self.key_frames.append((self.shots[i]+pre)//2)


	def get_key_frames(self):
		if len(self.key_frames) == 0:
			self.find_key_frames()

		frame_time_stamps = [i/self.fps for i in self.key_frames]
		return {
			"timestamps" : frame_time_stamps,
		}


	def save_key_frames(self):
		if len(self.key_frames) == 0:
			self.find_key_frames()	

		h = int(self.file.get(cv2.CAP_PROP_FRAME_HEIGHT))
		w = int(self.file.get(cv2.CAP_PROP_FRAME_WIDTH))

		codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
		self.out = cv2.VideoWriter(
			"[FabBits]"+self.filename+'.avi', cv2.CAP_FFMPEG, codec, 1, (w, h)
		)

		for fr in self.key_frames:
			self.file.set(1, fr-1)
			fr = self.file.read()[1]
			self.out.write(fr)

		self.out.release()


	def save(self):
		self.save_key_frames()
	

if __name__ == '__main__':
	
	import sys, os
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = DetectShots(file)
	shots = op.get_shots()
	
	with open('shot_boundaries_of_'+file+'.txt', 'w') as f:
		f.write(str(shots["timestamps"]))
		
	key_frames = op.get_key_frames()
	
	with open('key_frames_of_'+file+'.txt', 'w') as f:
		f.write(str(key_frames["timestamps"]))

	op.save()
