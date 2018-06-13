"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Detects action sequences
	Last updated - 10/06/2018

	TODO : MORE DATA!

"""

import pickle 
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips

from shot_detector import DetectShots
from motion_estimator import MotionEstimator
from helpers import HelperThread


class DetectAction():
	def __init__(self, file_path, clf_pickle="classifier.pkl"):
		super().__init__()
		self.file = VideoFileClip(file_path)
		self.file_path = file_path
		self.filename = file_path[file_path.rfind('/')+1:]
		
		self.action_timestamps = []
		with open(clf_pickle, "rb") as f:
			self.clf = pickle.load(f)


	def process(self):

		op1 = DetectShots(self.file_path)
		op1.process()

		shots = op1.get_shots()
		scenes = op1.get_scenes()
		shot_len = op1.get_average_shot_length()
		shot_cut = op1.get_shot_cut_freq()

		op2 = MotionEstimator(
			self.file_path, shots["frames"], scenes
		)
		op2.process()

		mo_int = op2.get_motion_intensity()
		cam_mo = op2.get_camera_motion()

		features = []
		for i in range(0, len(scenes)):
			features.append(
				[mo_int[i], cam_mo[i], shot_len[i], shot_cut[i]]
			)

		decision = self.clf.predict(np.array(features))

		action_shots = []
		for i in range(0, len(decision)) :
			if decision[i] == 1:
				if type(scenes[i]) == list:
					for shot in scenes[i]:
						action_shots.append(shot)
				else:
					action_shots.append(scenes[i])

		if len(action_shots) == 0:
			print("no action scenes!")
			return	

		action_shots.sort()

		action_clips = []
		self.action_timestamps = []
		for shot in action_shots:
			action_clips.append(
				self.file.subclip(
					shots["timestamps"][shot-1], shots["timestamps"][shot]
				)
			)
			self.action_timestamps.append({
				"s" : shots[shot-1], 
				"e" : shots[shot]
			})

		self.action = concatenate_videoclips(action_clips)
		

	def get_action_scenes(self):
		return {
			"timestamps" : self.action_timestamps
		}


	def save_action_scenes(self):
		self.action.write_videofile(
			"[FabBits] "+self.filename, codec=libx264
		)


	def save(self):
		self.save_action_scenes()

if __name__ == '__main__':
	import sys, os
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = DetectAction(file)
	op.process()

	action = op.get_action_scenes()
	print(action)

	op.save()