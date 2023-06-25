import cv2

vid = "C:\\nazim\Projects\machine_mindset\Youtube\GANs\\blinding_lights\\3.mp4"
cap = cv2.VideoCapture(vid)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('C:\\nazim\Projects\machine_mindset\Youtube\GANs\pre-made\distortion.mp4', fourcc, 10, (width, height))

for i in range(400):
    ret, frame = cap.read()
    if not ret:
        break

    out.write(frame)
