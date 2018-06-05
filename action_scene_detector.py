import sys

from motion_estimator import MotionEstimator
from shot_detector import DetectShots

op1 = DetectShots(sys.argv[1])
shots = op1.get_shots()["timestamps"]
op1.find_key_frames()
scenes = op1.get_scenes()

# print(shots)
# print(scenes)

op2 = MotionEstimator(sys.argv[1], shots, scenes)
op2.process()

with open("mo.txt", "w") as f:
	f.write(str(op2.get_motion_intensity()))

with open("cam.txt", "w") as f:
	f.write(str(op2.get_camera_motion()))