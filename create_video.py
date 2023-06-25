import cv2
import numpy as np
from PIL import Image, ImageFilter
import pillow_avif
import math
import os

from configs.create_video import IMG_PATH, DIVIDE_LINES, SUB_COLOR, BORDER_COLOR, X_DISP, Y_DISP, \
    TEXT_SIZE, TEXT_THICKNESS, FONT_FACE, DEBUG, DELAY_SUB_TIME, TEXT_PROMPT

ADD_NOISE = True
ADD_PIXELATION = True
ADD_DISTORTION = True
ADD_TEXT_PROMPTS = True

text_height = 50
def draw_subtitle(frame, texts):
    for i, text in enumerate(texts):
        # text_size, _ = cv2.getTextSize(text, font_face, font_scale, font_thickness)
        # cv2.rectangle(frame, (x, y - text_size[1]), (x + text_size[0], y + text_size[1] // 2), (0, 0, 0), -1)
        text_size = cv2.getTextSize(text, FONT_FACE, TEXT_SIZE, TEXT_THICKNESS)[0]
        frame_y, frame_x = frame.shape[0], frame.shape[1]
        text_x = int((frame_x - text_size[0]) / 2) + X_DISP
        num_text = len(texts)
        if num_text > 1:
            text_y = int(frame_y * 0.5 - num_text * text_height/2 + i * text_height) + Y_DISP
        else:
            text_y = int(frame_y * 0.5) + Y_DISP

        for c in text:
            if not c.isascii():
                text = text.replace(c, "")
        # draw text border
        cv2.putText(frame, text, (text_x, text_y), FONT_FACE, TEXT_SIZE, BORDER_COLOR, TEXT_THICKNESS + 1, cv2.LINE_AA)
        # draw text
        cv2.putText(frame, text, (text_x, text_y), FONT_FACE, TEXT_SIZE, SUB_COLOR, TEXT_THICKNESS, cv2.LINE_AA)

def apply_distortion(image, frame_number):
    rows, cols = image.shape[:2]
    shift = frame_number * 3
    # Creating a sinusoidal wave
    img_output = np.zeros(image.shape, dtype=image.dtype)
    for i in range(rows):
        for j in range(cols):
            offset_x = int(25.0 * np.sin(2 * 3.14 * i / 180))
            offset_y = 0
            if j+offset_x < rows:
                img_output[i,j] = image[(i+offset_x)%rows,j]
            else:
                img_output[i,j] = 0
    return img_output

if __name__ == "__main__":
    # convert image
    orig_img = Image.open(IMG_PATH)
    img_dir = os.path.dirname(IMG_PATH)
    new_path = IMG_PATH.replace(".avif", ".png")
    orig_img.save(new_path)
    final_image = cv2.imread(new_path)

    # read the distortion video
    distortion_video = 'C:\\nazim\Projects\machine_mindset\Youtube\GANs\pre-made\distortion.mp4'
    distortion_cap = cv2.VideoCapture(distortion_video)

    # create output video
    height, width, _ = final_image.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(os.path.join(img_dir, "output.mp4"), fourcc, 10.0, (width, height))

    num_frames = 200  # Modify this variable to change the number of frames in the video
    last_distortion_frame = None
    distortion_end_frame_num = num_frames / 6

    for i in range(num_frames):
        if i % 100 == 0:
            print(f"Wrote: {i} frames")
        frame = final_image.copy()

        if ADD_NOISE:
            noise_percent = ((num_frames - i) / num_frames) * 2
            if noise_percent <= 0.05:
                noise_percent = 0
            noise = np.random.normal(0, noise_percent, frame.shape).astype(np.uint8)
            frame = cv2.add(frame, noise)

        if ADD_PIXELATION:
            scale_percent = max(1, i)
            if i <= num_frames * 9 / 10:
                scale_percent /= 2
                scale_percent = max(1, scale_percent)

            scaled_width = int(frame.shape[1] * scale_percent / num_frames)
            scaled_height = int(frame.shape[0] * scale_percent / num_frames)
            dim = (scaled_width, scaled_height)
            small = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            frame = cv2.resize(small, (frame.shape[1], frame.shape[0]), interpolation = cv2.INTER_AREA)

        if ADD_DISTORTION:
            ret, distortion_frame = distortion_cap.read()
            # use last one when video ends
            if ret:
                last_distortion_frame = distortion_frame
            else:
                distortion_frame = last_distortion_frame
            

            # add it to frame and mask
            distortion_frame = cv2.resize(distortion_frame, (width, height))
            # Calculate the alpha value for blending (range from 1 to 0)
            alpha = max(0, (distortion_end_frame_num - i) / distortion_end_frame_num)
            # Blend the distortion frame with the final image
            frame = cv2.addWeighted(distortion_frame, alpha, frame, 1 - alpha, 0)

        if ADD_TEXT_PROMPTS:
            draw_subtitle(frame, [TEXT_PROMPT])

        video.write(frame)

    video.release()