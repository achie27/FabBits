import cv2
import pickle
import tesserocr
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, concatenate_videoclips
from matplotlib import pyplot as plt

class Detect3Pointers():
	def __init__(self, file_path, ssim_pickle="ssim.pkl"):
		self.file = cv2.VideoCapture(file_path)
		self.fps = self.file.get(cv2.CAP_PROP_FPS)
		self.file_path = file_path
		self.filename = file_path[file_path.rfind('/')+1:]

		with open(ssim_pickle, "rb") as f:
			self.compare_ssim = pickle.load(f) 

		self.tpointers = []

	def process(self):
		
		random_frames = []
		frame_nos, n = [], 30*60*self.fps

		self.file.set(1, n)
		for x in range(0, 120):
			random_frames.append([self.file.read()[1], self.file.read()[1]])
			frame_nos.append(n)
			for _ in range(0, int(self.fps-1)):
				self.file.read()
			
			n+=self.fps+1

		frame_diff = []

		for i in range(0, len(random_frames)):
			frame_diff.append(
				cv2.cvtColor(
					random_frames[i][0], cv2.COLOR_BGR2GRAY
				) 
				- 
				cv2.cvtColor(
					random_frames[i][1], cv2.COLOR_BGR2GRAY
				)
			)

		ref_scoreboard_area = 33*390
		ref_scoreboard_asp = 390/33

		cand = []
		for k in range(0, len(frame_diff)):
			fr = frame_diff[k]
			w = cv2.Sobel(fr, cv2.CV_8U, 1,  0, ksize = 3)
			bl = cv2.blur(w, (5, 5))
			th_val, th = cv2.threshold(bl, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
			el= cv2.getStructuringElement(cv2.MORPH_RECT, (15, 10))
			morph = cv2.morphologyEx(th, cv2.MORPH_CLOSE, el)
			
			for i in range(0, morph.shape[0]):
				for j in range(0, morph.shape[1]):
					if morph[i][j]:
						morph[i][j] = 0
					else:
						morph[i][j] = 255

			_, contour, __ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

			for x in contour:
				rec = cv2.minAreaRect(x)
				box = np.int0(cv2.boxPoints(rec))
				ar = np.abs((box[2][0]-box[0][0]) * (box[0][1] - box[2][1]))

				a1, a2 = min(box[0][0], box[2][0]), max(box[0][0], box[2][0]) 
				b1, b2 = min(box[0][1], box[2][1]), max(box[0][1], box[2][1])
				asr = (a2-a1)/(b2-b1)
				
				cond1 = ar >= ref_scoreboard_area-1000 and ar <= ref_scoreboard_area + 1000
				cond2 = asr >= ref_scoreboard_asp-1 and asr <= ref_scoreboard_asp + 1
				if cond1 and cond2:
					cand.append([box, k])
					break

		cand.sort(key = lambda box: np.abs((box[0][0][1] - box[0][2][1])))
		cand = cand[0]
		print("got scoreboard area")

		x1, x2 = min(cand[0][0][0], cand[0][2][0]), max(cand[0][0][0], cand[0][2][0]) 
		y1, y2 = min(cand[0][0][1], cand[0][2][1]), max(cand[0][0][1], cand[0][2][1])

		self.file.set(1, frame_nos[cand[1]]-1)
		scoreboard_col = self.file.read()[1]
		scoreboard_col = scoreboard_col[y1:y2, x1+10:x2-10]
		scoreboard = cv2.cvtColor(scoreboard_col, cv2.COLOR_BGR2GRAY)
	
		self.file.set(1, 10*60*self.fps)
		q, init_scrbd = 5*60*25, 0

		while True:
			q+=1
			suc, fr = self.file.read()
			if not suc:
				break
			
			fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)	
			cr = fr[y1:y2, x1+10:x2-10]
				
			sim, img = self.compare_ssim(scoreboard, cr, full=True)
			
			if sim >= 0.85:
				init_scrbd = cr.copy()
				break

		print("got reference scoreboard")

		sim, img = self.compare_ssim(scoreboard, init_scrbd, full = True)

		sb = img.copy()
		for i in range(len(sb)):
			for j in range(len(sb[i])):
				if sb[i][j] >= 0.7:
					sb[i][j] = 0
				else:
					sb[i][j] = 255

		sb = sb.astype("uint8")
		_, cnt, __ = cv2.findContours(sb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		bbox= []
		for i in cnt:
			rec = cv2.minAreaRect(i)
			box = cv2.boxPoints(rec)
			box = np.int0(box)
			ar = np.abs((box[2][0]-box[0][0]) * (box[0][1] - box[2][1]))
			if ar == 0:
				continue
			
			asp = np.abs((box[2][0]-box[0][0]) / (box[0][1] - box[2][1]))
			c1 = ar <= 600 and ar >= 200
			c2 = asp <= 2 and asp >= 0.8
			if c1 and c2:
				bbox.append(box)

		a1, a2 = min(bbox[0][0][0], bbox[0][2][0]), max(bbox[0][0][0], bbox[0][2][0]) 
		b1, b2 = min(bbox[0][0][1], bbox[0][2][1]), max(bbox[0][0][1], bbox[0][2][1])
		c1, c2 = min(bbox[1][0][0], bbox[1][2][0]), max(bbox[1][0][0], bbox[1][2][0]) 
		d1, d2 = min(bbox[1][0][1], bbox[1][2][1]), max(bbox[1][0][1], bbox[1][2][1])

		print("got score regions")
		print("searching for three pointers")

		p, last = 0, 0
		pre1, pre2 = 0, 0
		self.file.set(1, 0)
		while True:
			suc, frame = self.file.read()
			if not suc: break
			p+=1
			if p - last >= 125:
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				sim = self.compare_ssim(gray[y1:y2, x1+10:x2-10], scoreboard, full=True)
				last = p
				if sim[0] >= 0.80:
					sc1, sc2 = 0, 0
					
					x = cv2.cvtColor(frame[y1:y2, x1+10:x2-10][b1:b2, a1:a2], cv2.COLOR_BGR2RGB)
					xx = cv2.copyMakeBorder(x, 50, 50, 50, 25, cv2.BORDER_WRAP)
					im = Image.fromarray((xx))
					im = im.resize((im.size[0]*20, im.size[1]*20), Image.ANTIALIAS)
					
					s1 = tesserocr.image_to_text(im)
					o = s1.split('\n')
					while '' in o:
						o.remove('')
					
					first = ''
					second = ''
					fl1, fl2 = True, True

					if len(x[0]) == 7:
						first = o[3]
						fl1 = False

					r = first.split(' ')
					if fl1 and len(r) == 4:
						sc1 = int(r[0])
					else:
						if len(o) > 1 and len(o[1]) >= 2 and o[1][0].isdigit():
							pos = str(o[1:]).find(o[1][0])
							sc1= int(o[1][0]) 
							if not o[1][0] == o[1][1]: 
								if str(o[1][0:pos]).isdigit():
									sc1 = int(o[1][0:pos])
			
						if not sc1 == 0:
							if sc1-pre1 > 3:
								if sc1 % 10 == 7 or sc1 % 10 == 9:
									tmp = sc1 - pre1 - 5
									if tmp <= 3 and tmp >= 0:
										sc1 = sc1-5

							elif sc1-pre1 < 0:
								if sc1 % 10 == 2 or sc1 % 10 == 4:
									tmp = sc1 - pre1 + 5
									if tmp <= 3 and tmp >= 0:
										sc1 = sc1+5
						
						elif sc1 == 0:
							sc1 = pre1

					y = cv2.cvtColor(frame[y1:y2, x1+10:x2-10][d1:d2, c1:c2], cv2.COLOR_BGR2RGB)
					yy = cv2.copyMakeBorder(y, 50, 50, 50, 25, cv2.BORDER_WRAP)
					im = Image.fromarray((yy))
					im = im.resize((im.size[0]*20, im.size[1]*20), Image.ANTIALIAS)

					s1 = tesserocr.image_to_text(im)
					o = s1.split('\n')
					while '' in o:
						o.remove('')

					if len(x[1]) == 7:    
						second = o[3]
						fl2 = False

					r = second.split(' ')
					if fl2 and len(r) == 4:
						sc2 = int(r[0])
					else:
						if len(o) > 1 and len(o[1]) >= 2 and o[1][0].isdigit():
							pos = str(o[1:]).find(o[1][0])
							sc2 = int(o[1][0]) 
							if not o[1][0] == o[1][1]: 
								if str(o[1][0:pos]).isdigit():
									sc2 = int(o[1][0:pos])


						if not sc2 == 0:
							if sc2-pre2 > 3:
								if sc2 % 10 == 7 or sc2 % 10 == 9:
									tmp = sc2 - pre2 - 5
									if tmp <= 3 and tmp >= 0:
										sc2 = sc2-5

							elif sc2-pre2 < 0:
								if sc2 % 10 == 2 or sc2 % 10 == 4:
									tmp = sc2 - pre2 + 5
									if tmp <= 3 and tmp >= 0:
										sc2 = sc2+5

						elif sc2 == 0:
							sc2 = pre2


					if sc1-pre1 == 3 or sc2 - pre2 == 3:
						self.tpointers.append(p)

					pre1, pre2 = sc1, sc2


	def get_3_pointers(self):
		return self.tpointers


	def get_timestamps(self):
		tpointers = []
		for tp in self.tpointers:
			tpointers.append({
				's' : tp/self.fps - 15,
				'e' : tp/self.fps + 2
			})

		return {
			"timestamps" : tpointers,
			"duration" :  self.file.get(cv2.CAP_PROP_FRAME_COUNT)/self.fps
		}


	def save_3ps(self):
		tpointers = []
		mp_file = VideoFileClip(self.file_path)
		for tp in self.tpointers:
			tpointers.append(
				mp_file.subclip(tp/self.fps-15, tp/self.fps+2)
			)

		tpointers = concatenate_videoclips(tpointers)
		tpointers.write_videofile('[FabBits] ' + self.filename, codec='libx264')


	def save(self):
		self.save_3ps();


if __name__ == '__main__':
	import os, sys
	file = sys.argv[1]
	if not os.path.isfile(file):
		print("There is no " + file +"!")
		sys.exit()

	op = Detect3Pointers(file)
	op.process()

	goals = op.get_3_pointers()
	print(goals)

	op.save()

