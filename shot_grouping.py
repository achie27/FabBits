"""
	Archit Mathur
	github.com/achie27
	architmathur2011@gmail.com

	Detects shot boundaries and groups them into scenes
	Last updated - 27/05/2018

	TODO : Make it modular and actually usable

"""

import cv2
import numpy as np 
	
INF = 100
k, i, N = 5, 0, 320*240
a, b, s = 0.2, 0.1, 4
hist, fd, shots = [], [], []
file = cv2.VideoCapture(sys.argv[1])
T = int(file.get(cv2.CAP_PROP_FPS) * 90)

while file.isOpened():
	suc, fr = file.read()
	if not suc:
		break
	fr = cv2.resize(fr, (320, 240))

	# gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
	# hist_fr = cv2.calcHist([gray_fr], [0], None, [256], [0, 256])

	b_fr = cv2.calcHist([fr], [0], None, [256], [0, 256])
	g_fr = cv2.calcHist([fr], [1], None, [256], [0, 256])
	r_fr = cv2.calcHist([fr], [2], None, [256], [0, 256])
	if i >= k:
		tmp1 = np.abs(b_fr - hist[i-k]['b'])/(2*N)
		tmp2 = np.abs(g_fr - hist[i-k]['g'])/(2*N)
		tmp3 = np.abs(r_fr - hist[i-k]['r'])/(2*N)
		fd.append(
			np.sum(tmp1+tmp2+tmp3)/3
		) 
	hist.append({
		'b' : b_fr,
		'g' : g_fr,
		'r' : r_fr
	})
	i+=1
print('frames and hist created')
print(len(fd))
cnt = 0
total_frames = i
print(i)
print(fd)
print(np.mean(fd))

diff_fd = np.diff(fd)
for i in range(2, total_frames-k):	#skipping the first 2 frames
	if fd[i]>a and diff_fd[i-1]>diff_fd[i-2] and diff_fd[i-1]>diff_fd[i] :
		#frames that are the starting boundaries of shots
		shots.append(i + k)
	else :
		if fd[i] > b and fd[i-1]>b:
			cnt+=1
		else:
			cnt=0
		if cnt>=s:
			cnt = 0
			shots.append(i + k - s) 

print('shots found')

key_frames = []
total_shots = len(shots)
for i in range(0, total_shots):
	pre = i == 0 and 0 or shots[i-1]
	#randomly taking the mid one as the key frame
	key_frames.append((shots[i]+pre)//2)

print('key frames found')

D, delta = [], 0.3
for i in range(0, total_shots):
	lim, j = key_frames[i] + T, i+1
	while j < total_shots and key_frames[j] <= lim:
		D.append({
			'f1' : i,
			'f2' : j,
			'fd' : np.sum(np.abs(hist[j] - hist[i]))/(2*N),
		})
		j+=1

print('differences calculated')

#for union find
shot_scene = [ i for i in range(0, total_shots)]
D.sort(key = lambda obj: obj['fd'])
for ob in D:
	if ob['fd']>delta:
		break
	shot_scene[ob['f1']] = ob['f1']
	shot_scene[ob['f2']] = ob['f1']

print('grouped into scenes')

#union find path compression
def compress_path(index):
	if shot_scene[index] == index:
		return 
	compress_path(shot_scene[index])
	shot_scene[index] = shot_scene[shot_scene[index]]

for i in range(0, total_shots):
	compress_path(i)

print(shots)
print(shot_scene)