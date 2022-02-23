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
 
capture.release()