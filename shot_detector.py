"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Detects shot boundaries and groups them into scenes
	Last updated - 13/06/2018

	TODO : Make key frame extraction better

"""

import cv2
import numpy as np 
import multiprocessing as mp
from helpers import search, HelperThread
from moviepy.editor import ImageSequenceClip

class DetectShots():
	def __init__(self, file_path):
		self.frame_diff_interval, self.total_pixels = 10, 320*240 
		self.shot_similarity_threshold, self.abrupt_trans_cnt = 3, 8
		self.upper_bound, self.lower_bound,  = 0.45, 0.25

		self.hist, self.fd, self.shots, = [], [], []
		self.total_shots, self.total_frames = 0, 0
		self.key_frames, self.out, self.D = [], [], []
		self.shot_scene, self.scenes = [], []
		self.avg_shot_length, self.shot_cut_freq = [], []

		self.file_path = file_path
		self.file = cv2.VideoCapture(file_path)
		self.filename = file_path[file_path.rfind('/')+1:]
		self.fps = self.file.get(cv2.CAP_PROP_FPS)
		self.T = int(self.fps * 150)	#2.5min


	# def multiprocessed_fd_calc(self):

	# 	self.total_frames = int(self.file.get(cv2.CAP_PROP_FRAME_COUNT))
	# 	with mp.Pool(4) as p:
	# 		a = p.apply_async(
	# 			calc_frame_diff_v2,
	# 			args=(1, self.total_frames//4, self.file_path, self.frame_diff_interval, 1, self.total_pixels)
	# 		)

	# 		b = p.apply_async(
	# 			calc_frame_diff_v2,
	# 			args=(self.total_frames//4, self.total_frames//2, self.file_path, self.frame_diff_interval, 2, self.total_pixels)
	# 		)

	# 		c = p.apply_async(
	# 			calc_frame_diff_v2,
	# 			args=(self.total_frames//2, 3*self.total_frames//4, self.file_path, self.frame_diff_interval, 3, self.total_pixels)
	# 		)

	# 		d = p.apply_async(
	# 			calc_frame_diff_v2,
	# 			args=(3*self.total_frames//4, self.total_frames, self.file_path, self.frame_diff_interval, 4, self.total_pixels)
	# 		)

	# 		p.close()
	# 		p.join()

	# 	print("its done")
	# 	res1, res2, res3, res4 = a.get(), b.get(), c.get(), d.get()
	# 	self.fd = res1["fd"] + res2["fd"] + res3["fd"] + res4["fd"]
	# 	self.hist = res1["hist"] + res2["hist"] + res3["hist"] + res4["hist"]



	def multithreaded_fd_calc(self):
		"""
		Creates threads and file pointers for multithreading frame
		difference calculation

		"""

		self.total_frames = int(self.file.get(cv2.CAP_PROP_FRAME_COUNT))
		self.hist = [0]*self.total_frames
		self.fd = [0]*self.total_frames

		# need different file pointers for multithreading
		tmp_file1 = cv2.VideoCapture(self.file_path)
		tmp_file2 = cv2.VideoCapture(self.file_path)

		# each function processes a third of the file
		f1 = lambda : self.calc_frame_diff(
			1, self.total_frames//3, self.file
		)
		f2 = lambda : self.calc_frame_diff(
			self.total_frames//3, 2*self.total_frames//3, tmp_file1
		)
		f3 = lambda : self.calc_frame_diff(
			2*self.total_frames//3, self.total_frames, tmp_file2
		)

		a = HelperThread("Frame Difference 1", f1) 
		b = HelperThread("Frame Difference 2", f2) 
		c = HelperThread("Frame Difference 3", f3)
		a.start(), b.start(), c.start()
		a.join(), b.join(), c.join()

		tmp_file2.release(), tmp_file1.release()


	
	def calc_frame_diff(self, st, end, file):
		"""
		Calculates the histogram difference between frames 
		self.frame_diff_interval apart. Helps detect shot boundaries.

		"""

		# set the opencv file pointer to read frame no st next
		file.set(1, st-1)

		# housekeeping
		counter = max(0, st-1)

		# iterate for the entire range of frames (st, end)
		while file.isOpened() and counter < end:
			suc, fr = file.read()
			if not suc : break

			fr = cv2.resize(fr, (320, 240))
			gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)

			# the frame's histogram
			hist_fr = cv2.calcHist(
				[gray_fr], [0], None, [256], [0, 256]
			)

			# save the histogram/frame diff -
			# calculating it for frames self.frame_diff_interval apart
			# helps detect both gradual and abrupt transitions
			if counter >= self.frame_diff_interval :
				tmp = np.abs(
					hist_fr-self.hist[counter-self.frame_diff_interval]
				)
				fd = np.sum(tmp)/(2*self.total_pixels)
				self.fd[counter-self.frame_diff_interval] = fd
				
			# save the histogram
			self.hist[counter] = hist_fr
			counter+=1


	def find_shots(self):
		"""
		Using the frame difference calculated before, it finds shot 
		boundaries and saves the end frame no. of each shot in
		self.shots.

		"""
		
		counter = 0
		
		# a local maxima in FD indicates a potential gradual transition
		diff_fd = np.diff(self.fd)

		# iterate!
		for i in range(2, self.total_frames):

			# naively checking for local maxima
			# in diff_fd, x corresponds to x-1 
			local_max=diff_fd[i-1]>diff_fd[i-2] and diff_fd[i-1]>diff_fd[i]
			
			# if this FD is above a threshold and a local max, it
			# corresponds to a gradual transition boundary
			if self.fd[i] > self.upper_bound and local_max :

				# add only if shots are 8s apart 
				if not search(self.shots, int(i-self.fps*8), int(i+self.fps*8)):
					self.shots.append(i - self.frame_diff_interval)
			
			# check for abrupt transition boundary
			else :		

				# if a series of FD are above a certain threshold, it
				# is an abrupt transition
				if self.fd[i] > self.lower_bound and self.fd[i-1] > self.lower_bound:
					counter += 1
				else:
					counter = 0

				if counter >= self.abrupt_trans_cnt :
					counter = 0
					if not search(self.shots, i-self.fps*8, i+self.fps*8):
						self.shots.append(i - self.abrupt_trans_cnt - self.frame_diff_interval)

		self.total_shots = len(self.shots) 


	def find_key_frames(self):

		self.key_frames = []
		
		with mp.Pool(4) as p:

			args = [self.shots, self.hist, self.total_pixels]

			a=p.apply_async(
				find, 
				args=(
					*args, 0, self.total_shots//2, 1, self.fps, 
				)
			)

			b=p.apply_async(
				find, 
				args=(
					*args, self.total_shots//2, self.total_shots, 2, self.fps, 
				)
			)
			
			p.close()
			p.join()

		self.key_frames = a.get() + b.get()


	def group_into_scenes(self):
		D = []

		for i in range(0, self.total_shots):
			lim, j = self.key_frames[i][0] + self.T, i+1
			while j < self.total_shots and self.key_frames[j][0] <= lim:
				tmp = np.array([[0]*256]).reshape((256, 1))
				for i_key_frame in self.key_frames[i]:
					for j_key_frame in self.key_frames[j]:
						x = np.abs(self.hist[i_key_frame] - self.hist[j_key_frame])
						tmp = tmp + x

				tmp = np.sum(tmp) / (2*self.total_pixels)
				D.append({
					'f1' : i,
					'f2' : j,
					'fd' : tmp 
				})
				j+=1

		self.shot_scene = [i for i in range(0, self.total_shots)]
		D.sort(key = lambda o : o["fd"])
		for ob in D:
			if ob['fd'] > self.shot_similarity_threshold:
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


	def process(self):
		"""
		This is what should be called to calculate stuff

		"""

		self.multithreaded_fd_calc()
		self.find_shots()
		self.find_key_frames()
		self.group_into_scenes()


	def get_shots(self):
		# convert = lambda a : a//60 + (a/60 - a//60)*0.6
		shots = [i/self.fps for i in self.shots]
		return {
			"timestamps" : shots,
			"frames" : self.shots
		}

	def get_key_frames(self):
		frame_time_stamps = []
		for shot in self.key_frames:
			frame_time_stamps.append([])
			for key_frame in shot:
				frame_time_stamps[-1].append(key_frame/self.fps)

		return {
			"timestamps" : frame_time_stamps,
			"frames" : self.key_frames
		} 

	def get_scenes(self):
		self.scenes = [[] for i in range(0, self.total_shots)]

		i = 0
		while i < self.total_shots :

			# the ith shot belongs to self.shot_scene[i] root shot
			self.scenes[self.shot_scene[i]].append(i)
			i = i + 1

		# removing shots that weren't root thus getting scenes
		while self.scenes.count([]) > 0:
			self.scenes.remove([])

		return self.scenes


	def get_average_shot_length(self):
		self.avg_shot_length, mx = [], 0
		tot_scene = len(self.scenes)
		for i in range(0, tot_scene):
			l, cnt = 0, 0
			for ob in self.scenes[i]:
				pre = 0 if ob == 0 else self.shots[ob-1]
				l += (self.shots[ob] - pre)
				cnt += 1
			
			l = l/cnt
			self.avg_shot_length.append(l)

		return np.array(self.avg_shot_length)


	def get_shot_cut_freq(self):
		self.shot_cut_freq = []
		for i in range(0, len(self.scenes)):
			self.shot_cut_freq.append(1/len(self.scenes[i]))

		return self.shot_cut_freq


	def save_key_frames(self):
		frame_list = []
		for shot in self.key_frames:
			for fr in shot:
				self.file.set(1, fr-1)
				fr = np.array(self.file.read()[1])
				fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
				frame_list.append(fr)

		self.out = ImageSequenceClip(frame_list, fps=1)			
		self.out.write_videofile('[FabBits] '+self.filename, codec='libx264')


	def save(self):
		self.save_key_frames()


# def calc_frame_diff_v2(st, end, file_path, fd_interval, idn, total_pixels):
# 	"""
# 	Calculates the histogram difference between frames 
# 	self.frame_diff_interval apart. Helps detect shot boundaries.

# 	"""

# 	print(str(idn) +" has begun")

# 	file = cv2.VideoCapture(file_path)
	
# 	# set the opencv file pointer to read frame no st next
# 	file.set(1, st-1)

# 	frame_diff = [0]*(end-st)
# 	hist = [0]*(end-st)

# 	counter = max(0, st-1)

# 	# iterate for the entire range of frames (st, end)
# 	while file.isOpened() and counter < end:
# 		suc, fr = file.read()
# 		if not suc : 
# 			break

# 		fr = cv2.resize(fr, (320, 240))
# 		gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)

# 		# the frame's histogram
# 		hist_fr = cv2.calcHist(
# 			[gray_fr], [0], None, [256], [0, 256]
# 		)

# 		# save the histogram/frame diff -
# 		# calculating it for frames self.frame_diff_interval apart
# 		# helps detect both gradual and abrupt transitions
# 		if counter >= fd_interval :
# 			tmp = np.abs(
# 				hist_fr-hist[counter-fd_interval-st]
# 			)
# 			fd = np.sum(tmp)/(2*total_pixels)
# 			frame_diff[counter-fd_interval-st] = fd
			
# 		# save the histogram
# 		hist[counter-st] = hist_fr
# 		counter+=1

# 	print(str(idn) +" has ended")

# 	return {
# 		"hist" : hist,
# 		"fd" : frame_diff
# 	}


# can't be a class method since it is getting multiprocessed
# multiprocessing requires all the arguments to be pickle-able
# self.file, opencv's VideoCapture object, is not pickleable
def find(shots, hist, total_pixels, s, e, idn, fps):
	threshold = 0.4
	transition_offset = 30 #frames
	key_frames = [0]*(e-s)
	print(str(idn)+" has begun - find")
	for i in range(s, e):
		pre = 0 if i == 0 else shots[i-1]
		key_frames[i-s]=[pre+transition_offset]
		for fr in range(pre+transition_offset+1, shots[i]):
			flag = 1
			for kfr in key_frames[i-s]:
				dif = np.sum(np.abs(hist[kfr] - hist[fr]))/(2*total_pixels)
				if dif < threshold : flag = 0

			# different and 4 seconds apart
			if flag == 1 and (fr - key_frames[i-s][-1]) > 4*fps: 
				key_frames[i-s].append(fr)
		
		print(i)
	
	print(str(idn) + " is done")
	return(key_frames)



if __name__ == '__main__':

	import sys, os
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = DetectShots(file)
	op.process()
	shots = op.get_shots()
	
	with open('shot_boundaries_of_'+file[file.rfind('/')+1:]+'.txt', 'w') as f:
		f.write(str(shots["timestamps"]))
			
	key_frames = op.get_key_frames()
	with open('key_frames_of_'+file[file.rfind('/')+1:]+'.txt', 'w') as f:
		f.write(str(key_frames["timestamps"]))

	with open('scenes_of_'+file[file.rfind('/')+1:]+'.txt', 'w') as f:
		f.write(str(op.get_scenes()))

	with open('shot_lengths_of_'+file[file.rfind('/')+1:]+'.txt', 'w') as f:
		f.write(str(op.get_average_shot_length()))

	with open('shot_cut_freq_of_'+file[file.rfind('/')+1:]+'.txt', 'w') as f:
		f.write(str(op.get_shot_cut_freq()))

	op.save()