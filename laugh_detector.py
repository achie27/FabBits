"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Module for laughter detection from sitcoms
	Last updated - 13/06/2018

"""

import numpy as np
from scipy import signal
from moviepy.editor import VideoFileClip, concatenate_videoclips

class LaughDetector():
	def __init__(self, file_path):
		self.file = VideoFileClip(file_path)
		self.filename = file_path[file_path.rfind('/')+1:]

		self.timestamps = []
		self.jokes = []

	def process(self):

		duration = int(self.file.duration)
		self.file = self.file.set_duration(duration)
		file_audio = self.file.audio

		# 10ms average ridiculously speeds this up 
		ten_ms_avg = lambda i, f: np.sqrt((f.subclip(i, i+0.01).to_soundarray()**2).mean()) 
		sig = [ten_ms_avg(i, file_audio) for i in np.arange(0.0, duration//1, 0.01)]

		sig_len = len(sig)

		freq = sig_len/duration
		t = np.arange(0, sig_len, 1)/freq

		# performing hilbert transform and finding the envelope 
		hil_sig = signal.hilbert(sig)
		sig_env = np.abs(hil_sig)

		# normalizing it
		avg = np.mean(sig_env)
		norm_env = [i/avg for i in sig_env]

		# smoothing the signal
		b, a = signal.butter(3, 0.05)
		smooth_env = signal.filtfilt(b, a, norm_env)

		#will find better ways to get this; although it works well
		high = 1.8
		low = 0.45

		self.timestamps, i = [{'s':0, 'e':0}], 0

		# the structure of laugh tracks is high at the beginning and
		# low at the end while gradually dying down in b/w
		while i < sig_len:
			if smooth_env[i] >= high :
				
				#merge if the previous joke is just 5s apart
				if self.timestamps[-1]['e'] >= t[i]-5:
					self.timestamps[-1]['e'] = np.min([t[i]+4, duration])

				# add new joke otherwise
				else :

					# adding 4 second buffers
					self.timestamps.append({
						's' : np.max([0, t[i]-4]),
						'e' : np.min([t[i]+4, duration])
					})
					
				# find the end of the joke
				while i < sig_len and smooth_env[i] >= low:

					# less buffer because theres usually not much to
					# the joke once the laughter has stopped
					self.timestamps[-1]['e'] = np.min([t[i]+2, duration])
					i+=1

			i+=1


	def get_laughs(self):
		return {
			"timestamps" : self.timestamps,
		} 


	def get_timestamps(self):
		return {
			"timestamps" : self.timestamps,
			"duration" : int(self.file.duration)
		} 		


	def save_laughs(self):
		for obj in self.timestamps:
			self.jokes.append(self.file.subclip(obj['s'], obj['e']))
		
		self.jokes = concatenate_videoclips(self.jokes)
		self.jokes.write_videofile('[FabBits] '+self.filename, codec='libx264')


	def save(self):
		self.save_laughs()


if __name__ == "__main__":

	import sys, os
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = LaughDetector(file)
	op.process()
	laughs = op.get_laughs()
	print(laughs)	#do whatever
	op.save()