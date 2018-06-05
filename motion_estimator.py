import cv2
# import threading
import numpy as np
# cap = cv2.VideoCapture("gsoc_data/s1.avi")
# ret, frame1 = cap.read()
# frame1 = cv2.resize(frame1, (100, 100))
# prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
# # hsv = np.zeros_like(frame1)
# frames = []
# # hsv[...,1] = 255
# i=0
# while(1):
#     ret, frame2 = cap.read()
#     if not ret :
#     	break
#     print(i)
#     frame2 = cv2.resize(frame2, (100, 100))
#     nxt = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
#     # frames.append(nxt)
#     flow = np.array(cv2.calcOpticalFlowFarneback(prvs,nxt, None, 0.5, 3, 15, 3, 5, 1.2, 0))
#     # mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
#     # hsv[...,0] = ang*180/np.pi/2
#     # hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
#     # bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
#     # cv2.imshow('fsrame2',bgr)
#     # k = cv2.waitKey(30) & 0xff
#     # if k == 27:
#     #     break
#     # elif k == ord('s'):
#     #     cv2.imwrite('opticalfb.png',frame2)
#     #     cv2.imwrite('opticalhsv.png',bgr)
#     prvs = nxt
#     i+=1

# def process(m, n):
#     i = m + 1
#     while i <= n :
#         flow = cv2.calcOpticalFlowFarneback(
#             frames[i-1], frames[i], None, 0.5, 3, 15, 3, 5, 1.2, 0
#         )
#         i+=1


# class TheThread(threading.Thread):
#     def __init__(self, name, f):
#         super().__init__()
#         self.f = f
#         self.name = name

#     def run(self):
#         print("started "+self.name)
#         self.f()
#         print(self.name+" boi is done")


# l = len(frames)
# opflow = [0]*l
# t1 = TheThread("1", lambda : process(0, l//2))
# t2 = TheThread("2", lambda : process(l//2+1, l))
# t1.start()
# t2.start()
# print("oya")
# t1.join()
# t2.join()
# print("owari da")

class MotionEstimator():
	def __init__(self, file_path, shots, scenes):
		self.file = cv2.VideoCapture(file_path)
		self.shots, self.scenes = np.array(shots), scenes
		self.scene_motion_intensity = []
		self.scene_camera_motion = []

	def get_motion_intensity(self):
		return self.scene_motion_intensity

	def get_camera_motion(self):
		return self.scene_camera_motion

	def process(self):
		cur_scene = 0
		frame_count = 0
		camera_motion_frames = 0
		motion_intensity = 0

		suc, pre = self.file.read()
		if not suc : 
			pass

		pre = cv2.resize(pre, (100, 100))
		pre = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)

		while 1:
			if frame_count > self.shots[self.scenes[cur_scene][-1]]:
				print(frame_count)
				print(cur_scene)
				print(self.scenes[cur_scene][-1])
				print(self.shots[self.scenes[cur_scene][-1]])

				self.scene_motion_intensity.append(motion_intensity)
				self.scene_camera_motion.append(camera_motion_frames)

				cur_scene += 1
				camera_motion_frames = 0
				motion_intensity = 0

			if cur_scene >= len(self.scenes):
				break

			suc, nxt = self.file.read()
			if not suc :
				break

			nxt = cv2.resize(nxt, (100, 100))
			nxt = cv2.cvtColor(nxt, cv2.COLOR_BGR2GRAY)
			
			flow = cv2.calcOpticalFlowFarneback(
				pre, nxt, None, 0.5, 3, 15, 3, 5, 1.2, 0
			)

			if (flow==0).sum() < 1000 :	#less than 10%
				camera_motion_frames += 1

			motion_intensity += np.sum(np.abs(flow))

			frame_count += 1
	