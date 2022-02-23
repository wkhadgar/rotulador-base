<<<<<<< HEAD
import cv2 
 
video_path = "Path/to/video"
frames_path = "Path/to/frames"
capture = cv2.VideoCapture(video_path)
 
frameNr = 0
 
while (True):
 
    success, frame = capture.read()
 
    if success:
        cv2.imwrite(frames_path + f'/frame_{frameNr:06d}.jpg', frame)
 
    else:
        break
 
    frameNr = frameNr+1
 
=======
import cv2 
 
video_path = "Path/to/video"
frames_path = "Path/to/frames"
capture = cv2.VideoCapture(video_path)
 
frameNr = 0
 
while (True):
 
    success, frame = capture.read()
 
    if success:
        cv2.imwrite(frames_path + f'/frame_{frameNr:06d}.jpg', frame)
 
    else:
        break
 
    frameNr = frameNr+1
 
>>>>>>> 897f6ac04fc69a9fe9e5a3bc3564c1961572d68f
capture.release()