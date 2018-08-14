"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Module for detecting goals from full length soccer videos
	Last updated - 05/07/2018

"""

import cv2
import pickle
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips

class DetectGoal():
	def __init__(self, file_path, ssim_pickle="ssim.pkl"):
		self.file = cv2.VideoCapture(file_path)
		self.fps = self.file.get(cv2.CAP_PROP_FPS)
		self.file_path = file_path
		self.filename = file_path[file_path.rfind('/')+1:]

		# compare_ssim is originally from skimage
		# didn't want to create another dependency so pickled it
		with open(ssim_pickle, "rb") as f:
			self.compare_ssim = pickle.load(f) 

		self.goals = []


	def process(self):

		# search this period for the frame with min edge intensity
		# a frame like that will make the scoreboard more distinguishable
		l, r = 15*self.fps*60, 35*self.fps*60
		self.file.set(1, l)
		min_thres, min_thres_frame = 100000, 0
		data = []
		
		while l <= r:
			suc, fr = self.file.read()
			fr = cv2.resize(fr, (500, 500))
			fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
			ed = cv2.Sobel(fr, cv2.CV_8U, 1, 0, ksize=3)
			bl = cv2.blur(ed, (5, 5))
			th_val, th = cv2.threshold(bl, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
			data.append({
				"fr" : l,
				"val" : (th==255).sum()
			})
			l+=1

		data.sort(key = lambda ob : ob["val"])
		min_thres_frame = data[0]['fr']
		del data

		#getting all the different items in the frame
		self.file.set(1, min_thres_frame)
		sc = self.file.read()[1]
		fr = cv2.cvtColor(sc, cv2.COLOR_BGR2GRAY)
		fr = cv2.resize(fr, (500, 500))
		ed = cv2.Sobel(fr, cv2.CV_8U, 1, 0, ksize=3)
		bl = cv2.blur(ed, (5, 5))
		th_val, th = cv2.threshold(bl, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
		el= cv2.getStructuringElement(cv2.MORPH_RECT, (15, 10))
		morph = cv2.morphologyEx(th, cv2.MORPH_CLOSE, el)
		_, contour, __ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)


		# area and aspect ratio of most scoreboards 		
		ar_lim = 3000
		asp_lim = 5.5

		#finding item that could potentially be the scoreboard
		bb = []
		for i in contour:
			rec = cv2.minAreaRect(i)
			box = cv2.boxPoints(rec)
			box = np.int0(box)
			ar = np.abs((box[2][0]-box[0][0]) * (box[0][1] - box[2][1]))
			if ar == 0:
				continue
			asp = np.abs((box[2][0]-box[0][0]) / (box[0][1] - box[2][1]))
			c1 = ar <= ar_lim + 1500 and ar >= ar_lim - 1000
			c2 = asp <= asp_lim + 1.5 and asp >= asp_lim - 1.5
				
			if c1 and c2:
				bb.append(box)


		#corner points of the scoreboard
		x1, x2 = min(bb[0][0][0], bb[0][2][0]), max(bb[0][0][0], bb[0][2][0]) 
		y1, y2 = min(bb[0][0][1], bb[0][2][1]), max(bb[0][0][1], bb[0][2][1])
		del contour
		del bb

		# getting the portion with the timer
		self.file.set(1, min_thres_frame+self.fps)
		nfr = self.file.read()[1]
		nfr = cv2.cvtColor(nfr, cv2.COLOR_BGR2GRAY)
		nfr = cv2.resize(nfr, (500, 500))
		nfr = nfr[y1:y2, x1:x2]

		# comparing frames that are a second apart
		# there difference will give the part of timer that changes
		# allowing the removal of timer altogether
		sim, img = self.compare_ssim(fr[y1:y2, x1:x2], nfr, full=True)
		sb = img.copy()
		for i in range(len(sb)):
			for j in range(len(sb[i])):
				if sb[i][j] >= 0.7:
					sb[i][j] = 0
				else:
					sb[i][j] = 255

		sb = sb.astype("uint8")
		_, cnt, __ = cv2.findContours(sb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		# getting the coordinates of the rectangular bound of changed digit(s)
		bbox = []
		for i in cnt:
			rec = cv2.minAreaRect(i)
			box = cv2.boxPoints(rec)
			box = np.int0(box)
			ar = np.abs((box[2][0]-box[0][0]) * (box[0][1] - box[2][1]))
			if ar == 0:
				continue
			asp = np.abs((box[2][0]-box[0][0]) / (box[0][1] - box[2][1]))
			c1 = ar <= 200 and ar >= 50
			c2 = asp <= 0.6 and asp >= 0.25

			if c1 and c2:
				bbox.append(box)

		# getting scoreboard area without the timer
		far_right = max(bbox[0][:,0])
		far_left = min(bbox[0][:,0])-20
		right = True

		if far_right <= sb.shape[1]/2:
			goals = nfr[:, far_right:]
		elif far_left >= sb.shape[1]/2:
			goals = nfr[:, :far_left]
			right = False		

		del bbox

		print("secluded timer")

		# finding the edge content of scoreboard for later comparison
		edge_content = (cv2.Sobel(goals, cv2.CV_8U, 1, 0, ksize=3)).sum()
		self.file.set(1, 0)
		q = 0

		# finding the initial scoreboard; doesn't need to be at 0-0
		while True:
			q+=1
			suc, fr = self.file.read()
			if not suc:
				break
			
			fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
			fr = cv2.resize(fr, (500, 500))
			
			if right:
				cr = fr[y1:y2, x1:x2][:, far_right:]
			else:
				cr = fr[y1:y2, x1:x2][:, :far_left]
				
			sim, img = self.compare_ssim(goals, cr, full=True)
			
			if sim >= 0.8:
				break

		print("found initial scoreboard")

		# using the initial scoreboard and the previosly segmented
		# scoreboard to get a similarity measure between the two
		a = self.file.read()[1]
		a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
		a = cv2.resize(a, (500, 500))
		if right:
			a = a[y1:y2, x1:x2][:, far_right:]
		else:
			a = a[y1:y2, x1:x2][:, :far_left]
			
		ssim, d = self.compare_ssim(goals, a, full=True)    
		# saving frames that differ from each other by a threshold
		pfr = self.file.read()[1]
		pfr = cv2.resize(pfr, (500, 500))
		if right:
			pfr = pfr[y1:y2, x1:x2][:, far_right:]
		else:
			pfr = pfr[y1:y2, x1:x2][:, :far_left]

		pfr = cv2.cvtColor(pfr, cv2.COLOR_BGR2GRAY)

		l = []
		while True:
			q+=1
			suc, fr = self.file.read()
			if not suc:
				break
			
			fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
			fr = cv2.resize(fr, (500, 500))
			
			if right:
				cr = fr[y1:y2, x1:x2][:, far_right:]
			else:
				cr = fr[y1:y2, x1:x2][:, :far_left]
			
			e = cv2.Sobel(cr, cv2.CV_8U, 1, 0, ksize=3)
			s = e.sum()
			
			# comparing edge content to only get the frames that have scoreboard 
			if s < edge_content + 1000 and s > edge_content - 1000:
				sim, img = self.compare_ssim(pfr, cr, full=True)

				# similarity comparison
				if sim <= ssim + 0.15 and sim >= ssim - 0.15:
					l.append([cr, q])

				pfr = cr.copy()

		# sequentially compare the found scoreboards to detect goals 
		g = [self.compare_ssim(l[i][0], l[i+1][0], full=True)[0] for i in range(0, len(l)-1)]
		goal = []
		
		# scoreboards with less than 87.5% similarity means that something has
		# changed; the only thing that can are the digits representing goals
		for i in range(len(g)):
			if g[i] <= 0.875:
				goal.append(l[i][1])

		# merge frames that are <=30s apart since they represent the same event
		# also most studios have a transition effect for score change
		# so this just merges them
		self.goals, i = [], 0
		while True:
			if i >= len(goal):
				break

			self.goals.append(goal[i])

			while i < len(goal)-1 and goal[i] + self.fps*30 >= goal[i+1]:
				i+=1

			i+=1
		

		
	def get_goals(self):
		"""
		Get frames that near a goal

		"""
		return self.goals


	def get_timestamps(self):
		goals = []
		for goal in self.goals:
			goals.append({
				's' : goal/self.fps-30,
				'e' : goal/self.fps+10
			})

		return {
			"timestamps" : goals,
			"duration" : self.file.get(cv2.CAP_PROP_FRAME_COUNT)/self.fps
		}


	def save_goals(self):
		goals = []
		mp_file = VideoFileClip(self.file_path)
		for goal in self.goals:
			goals.append(
				mp_file.subclip(goal/self.fps-30, goal/self.fps+10)
			)

		goals = concatenate_videoclips(goals)
		goals.write_videofile('[FabBits] '+self.filename, codec='libx264')


	def save(self):
		"""
		Save a video compilation

		"""
		self.save_goals()


if __name__ == '__main__':
	import os, sys
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = DetectGoal(file)
	op.process()

	goals = op.get_goals()
	print(goals)

	op.save()