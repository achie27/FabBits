"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Detects shot boundaries and groups them into scenes
	Last updated - 2/06/2018

	TODO : Make key frame extraction better

"""

import cv2
import numpy as np 
from helpers import search
from moviepy.editor import ImageSequenceClip

class DetectShots():
	def __init__(self, file_path):
		self.k, self.N, self.delta = 5, 320*240, 0.3
		self.a, self.b, self.s = 0.45, 0.25, 8
		self.hist, self.fd, self.shots, = [], [], []
		self.total_shots, self.total_frames = 0, 0
		self.key_frames, self.out, self.D = [], [], []
		self.shot_scene, self.scenes = [], []
		self.avg_shot_length, self.shot_cut_freq = [], []

		self.file = cv2.VideoCapture(file_path)
		self.filename = file_path[file_path.rfind('/')+1:]
		self.fps = self.file.get(cv2.CAP_PROP_FPS)
		self.T = int(self.fps * 300)


	def get_shots(self):
		self.find_frame_difference()
		self.find_shots()

		# shots = [i/self.fps for i in self.shots]
		return {
			"timestamps" : self.shots
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

		frame_list = []
		for fr in self.key_frames:
			self.file.set(1, fr-1)
			fr = np.array(self.file.read()[1])
			fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
			frame_list.append(fr)

		self.out = ImageSequenceClip(frame_list, fps=1)			
		self.out.write_videofile('[FabBits] '+self.filename, codec='libx264')


	def group_into_scenes(self):
		D = []
		for i in range(0, self.total_shots):
			lim, j = self.key_frames[i] + self.T, i+1
			while j < self.total_shots and self.key_frames[j] <= lim:
				tmp = np.sum(np.abs(self.hist[j] - self.hist[i])/(2*self.N))
				D.append({
					'f1' : i,
					'f2' : j,
					'fd' : tmp 
				})
				j+=1

		self.shot_scene = [i for i in range(0, self.total_shots)]
		D.sort(key = lambda o : o["fd"])
		for ob in D:
			if ob['fd'] > self.delta:
				break
			self.shot_scene[ob['f1']] = ob['f1']
			self.shot_scene[ob['f2']] = ob['f1']

		def path_compress(index, arr):
			if arr[index] == index:
				return 
			path_compress(arr[index], arr)
			arr[index] = arr[arr[index]]

		for i in range(0, self.total_shots):
			path_compress(i, self.shot_scene)

	# index == scene; corresponding list == shot indexes
	def get_scenes(self):
		self.group_into_scenes()
		self.scenes = [[] for i in range(0, self.total_shots)]

		i = 0
		while i < self.total_shots :
			self.scenes[self.shot_scene[i]].append(i)
			i = i + 1

		while self.scenes.count([]) > 0:
			self.scenes.remove([])

		return self.scenes


	def save(self):
		self.save_key_frames()
	

	def get_average_shot_length(self):
		self.avg_shot_length = []
		tot_scene = len(self.scenes)
		for i in range(0, tot_scene):
			l, cnt = 0, 0
			for ob in self.scene[i]:
				pre = 0 if ob == 0 else self.shots[ob-1]
				l += (self.shots[ob] - pre)
				cnt += 1
			
			l = l/cnt
			self.avg_shot_length.append(l)

		return self.avg_shot_length


	def get_shot_cut_freq(self):
		self.shot_cut_freq = []
		for i in range(0, len(self.scenes)):
			self.shot_cut_freq.append(1/len(self.scenes[i]))

		return self.shot_cut_freq


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

	# fr_diff = op.get_frame_differences()
	# with open('frame_diff_of_'+file+'.txt', 'w') as f:
	# 	f.write(str(fr_diff))

	# op.group_into_scenes()
	print(op.get_scenes())

	op.save()
