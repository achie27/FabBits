import cv2
import pickle
from shot_detector import DetectShots
from moviepy.editor import VideoFileClip, concatenate_videoclips


class DetectActor():
	def __init__(self, file_path, actor_label, clf = 'lbp.xml',
				faces = 'faces.pkl', labels = 'labels.pkl'):
		
		self.file = cv2.VideoCapture(file_path)
		self.file_path = file_path
		self.filename = file_path[file_path.rfind('/')+1 : ]
		self.fps = self.file.get(cv2.CAP_PROP_FPS)
		self.actor = int(actor_label)

		with open(faces, 'rb') as f:
			faces = pickle.load(f)

		with open(labels, 'rb') as f:
			labels = pickle.load(f)

		self.clf = cv2.CascadeClassifier(clf)
		self.recog = cv2.face.LBPHFaceRecognizer_create()
		self.recog.train(faces, labels)
		self.actor_shots = []
		self.shots = []


	def process(self):

		shot_object = DetectShots(self.file_path)
		shot_object.multithreaded_fd_calc()
		shot_object.find_shots()
		self.shots = shot_object.get_shots()['frames']

		for i in range(1, len(self.shots)):
			self.file.set(1, self.shots[i-1])
			
			face_found = False
			num = self.shots[i-1]
			while num < self.shots[i]:
				num+=1
				suc, fr = self.file.read()
				if not suc : break

				gr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
				gr = cv2.resize(gr, (400, 300))
				faces = self.clf.detectMultiScale(gr, scaleFactor=1.2, minNeighbors = 5)

				if len(faces) == 0:
					continue

				for face in faces:
					(x, y, w, h) = face

					if self.recog.predict(gr[y:y+w, x:x+h])[0] == self.actor:
						face_found = True
						break

				if face_found:
					break

			if face_found:
				self.actor_shots.append(i)

		print("Found shots with the actor.")


	def get_timestamps(self):
		
		ts = []
		for x in self.actor_shots:
			ts.append({
				's' : self.shots[x-1]/self.fps,
				'e' : self.shots[x]/self.fps
			})

		return {
			"timestamps" : ts,
			"duration" : self.file.get(cv2.CAP_PROP_FRAME_COUNT)/self.fps
		}


	def save(self):

		clips = []
		mp_file = VideoFileClip(self.file_path)
		for x in self.actor_shots:
			clips.append(
				mp_file.subclip(self.shots[x-1]/self.fps, self.shots[x]/self.fps)
			)

		clips = concatenate_videoclips(clips)
		clips.write_videofile('[FabBits] ' + self.filename, codec = 'libx264')


if __name__ == '__main__':
	
	a = DetectActor("aiw.mp4", 48)
	a.process()
	a.save()
	print(a.get_timestamps())