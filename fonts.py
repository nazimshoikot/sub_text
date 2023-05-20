import cv2
import numpy as np

font_list = [
    cv2.FONT_HERSHEY_SIMPLEX,
    cv2.FONT_HERSHEY_PLAIN,
    cv2.FONT_HERSHEY_DUPLEX,
    cv2.FONT_HERSHEY_COMPLEX,
    cv2.FONT_HERSHEY_TRIPLEX,
    cv2.FONT_HERSHEY_COMPLEX_SMALL,
    cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
]

font_names = [
    "FONT_HERSHEY_SIMPLEX",
    "FONT_HERSHEY_PLAIN",
    "FONT_HERSHEY_DUPLEX",
    "FONT_HERSHEY_COMPLEX",
    "FONT_HERSHEY_TRIPLEX",
    "FONT_HERSHEY_COMPLEX_SMALL",
    "FONT_HERSHEY_SCRIPT_SIMPLEX",
    "FONT_HERSHEY_SCRIPT_COMPLEX",
]

img = np.zeros((600, 800, 3), dtype=np.uint8)

for idx, font in enumerate(font_list):
    cv2.putText(img, f"{font_names[idx]} Example", (20, (idx + 1) * 60), font, 1, (255, 255, 255), 2)

cv2.imshow("OpenCV Fonts", img)
cv2.waitKey(0)
cv2.destroyAllWindows()