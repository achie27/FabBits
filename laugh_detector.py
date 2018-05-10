"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Module for laughter detection from sitcoms
	Last updated - 09/05/2018

"""

import numpy as np
from scipy import signal
from moviepy.editor import VideoFileClip, concatenate_videoclips

class LaughDetector():
	def __init__(self, file_path):
		self.file = VideoFileClip(file_path)
		self.timestamps = []

	def find_laughs(self):

		duration = int(self.file.duration)
		self.file = self.file.set_duration(duration)
		self.file = self.file.resize((320, 240))
		file_audio = self.file.audio

		ten_ms_avg = lambda i, f: np.sqrt((f.subclip(i, i+0.01).to_soundarray()**2).mean()) 
		sig = [ten_ms_avg(i, file_audio) for i in np.arange(0.0, duration//1, 0.01)]

		sig_len = len(sig)

		freq = sig_len/duration
		t = np.arange(0, sig_len, 1)/freq

		# performing hilbert transform and finding the envelope 
		hil_sig = signal.hilbert(sig)
		sig_env = np.abs(hil_sig)

		avg = np.mean(sig_env)
		norm_env = [i/avg for i in sig_env]

		b, a = signal.butter(3, 0.05)
		smooth_env = signal.filtfilt(b, a, norm_env)

		#will find better ways to get this; although it works well
		high = 1.8
		low = 0.45

		self.timestamps, clip, offset, i = [{'s':0, 'e':0}], 0, 0, 0
		while i < sig_len:
			if smooth_env[i] >= high :
				
				if self.timestamps[-1]['e'] >= t[i]-5:
					self.timestamps[-1]['e'] = np.min([t[i]+4, duration])
				else :
					# adding 4 second buffers
					self.timestamps.append({
						's' : np.max([0, t[i]-4]),
						'e' : np.min([t[i]+4, duration])
					})
					
				while i < sig_len and smooth_env[i] >= low:
					self.timestamps[-1]['e'] = np.min([t[i]+2, duration])
					i+=1

			i+=1

	def get_laughs(self):
		jokes = []
		for obj in self.timestamps:
			jokes.append(self.file.subclip(obj['s'], obj['e']))
		jokes = concatenate_videoclips(jokes)
		
		return {
			"timestamps" : self.timestamps,
			"bits" : jokes
		} 

if __name__ == "__main__":

	import sys, os
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = LaughDetector(file)
	op.find_laughs()
	laughs = op.get_laughs()
	laughs['bits'].write_videofile("jokes_in_"+file, codec='libx264')