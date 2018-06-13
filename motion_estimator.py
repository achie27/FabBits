"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Module for estimating motion using optical flow
	Last updated - 13/06/2018

"""

import cv2
import numpy as np
from helpers import HelperThread

class MotionEstimator():
	def __init__(self, file_path, shots, scenes):
		self.file_path = file_path
		self.file = cv2.VideoCapture(file_path)
		self.shots, self.scenes = np.array(shots), scenes
		self.scene_motion_intensity = []
		self.scene_camera_motion = []
		self.total_frames = 0

	def get_motion_intensity(self):
		return self.scene_motion_intensity

	def get_camera_motion(self):
		return self.scene_camera_motion


	def process(self):
		"""
		Multithreads the estimation of optical flow

		"""

		tot_scenes = len(self.scenes)

		# motion intensity is how much the objects inside the frame move
		# this holds how much intensity each scene has
		self.scene_motion_intensity = [0]*tot_scenes

		# camera motion occurs when the recording camera itself moves
		# this holds the number of frames in each scene that have
		# camera motion
		self.scene_camera_motion = [0]*tot_scenes

		# for multithreading
		tmp_file1 = cv2.VideoCapture(self.file_path)
		tmp_file2 = cv2.VideoCapture(self.file_path)

		f1 = lambda : self.estimate(0, tot_scenes//3, self.file)
		f2 = lambda : self.estimate(tot_scenes//3, 2*tot_scenes//3, tmp_file1)
		f3 = lambda : self.estimate(2*tot_scenes//3, tot_scenes, tmp_file2)

		t1 = HelperThread("Optical Flow 1", f1)
		t2 = HelperThread("Optical Flow 2", f2)
		t3 = HelperThread("Optical Flow 3", f3)

		t1.start(), t2.start(), t3.start()
		t1.join(), t2.join(), t3.join()

		tmp_file2.release()
		tmp_file1.release()


	def estimate(self, st, end, file):
		for i in range(st, end):
			camera_motion_frames = 0
			motion_intensity = 0

			for j in range(0, len(self.scenes[i])):

				# get the framewise shot boundary
				shot = self.scenes[i][j]
				prev_shot_bound = 0 if shot==0 else self.shots[shot-1]
				curr_shot_bound = self.shots[shot]			
				
				curr_frame = prev_shot_bound

				# move file pointer
				file.set(1, prev_shot_bound)
				suc, pre = file.read()
				if not suc : pass

				# optical flow is expensive to calculate
				pre = cv2.resize(pre, (100, 100))
				pre = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)

				while curr_frame < curr_shot_bound:
					suc, nxt = file.read()
					if not suc : break

					nxt = cv2.resize(nxt, (100, 100))
					nxt = cv2.cvtColor(nxt, cv2.COLOR_BGR2GRAY)

					# calculating optical flow with Farneback's Algorithm
					flow = cv2.calcOpticalFlowFarneback(
						pre, nxt, None, 0.5, 3, 15, 3, 5, 1.2, 0
					)

					# if there are less than 10% 0s in flow,
					# the frame has camera motion
					if (flow == 0).sum() < 1000 :
						camera_motion_frames += 1

					motion_intensity += np.sum(np.abs(flow))
					curr_frame += 1

			self.scene_motion_intensity[i] = motion_intensity
			self.scene_camera_motion[i] = camera_motion_frames

		# normalize
		self.scene_motion_intensity=np.array(self.scene_motion_intensity)
		mx = self.scene_motion_intensity.max()
		self.scene_motion_intensity=self.scene_motion_intensity/mx

		self.scene_camera_motion = np.array(self.scene_camera_motion)
		mx = self.scene_camera_motion.max()
		self.scene_camera_motion = self.scene_camera_motion / mx