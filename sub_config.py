import cv2

# FILES
VIDEO_FILE = "C:\\nazim\Projects\machine_mindset\Youtube\chatgpt_v_bard\short-v1.mp4" 
SRT_FILE = "C:\\nazim\Projects\machine_mindset\Youtube\chatgpt_v_bard\short_cap.srt"
OUT_DIR = "C:\\nazim\Projects\machine_mindset\Youtube\chatgpt_v_bard"

# PROCESSING
DIVIDE_LINES = True
DELAY_SUB_TIME = -0.5

# SUB STYLE
SUB_COLOR = (255, 255, 255)
BORDER_COLOR = (255, 0, 0) # bgr
X_DISP = 0
Y_DISP = 40
TEXT_SIZE = 1.0
TEXT_THICKNESS = 2
FONT_FACE = cv2.FONT_HERSHEY_COMPLEX

# PROGRAM MODE
DEBUG = False