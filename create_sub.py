from os import path
from datetime import datetime
import os
import sys

import cv2

from configs.sub_config import VIDEO_FILE, SRT_FILE, OUT_DIR, DIVIDE_LINES, SUB_COLOR, BORDER_COLOR, X_DISP, Y_DISP, \
    TEXT_SIZE, TEXT_THICKNESS, FONT_FACE, DEBUG, DELAY_SUB_TIME


def process_args():
    vid = VIDEO_FILE
    srt = SRT_FILE
    out_dir = OUT_DIR
    
    # check that the filepath exists
    for filepath in [vid, srt, out_dir]:
        if not path.exists(filepath):
            print(f"{filepath} does not exist")
            sys.exit(1)
    
    # get displacements
    x_disp = X_DISP
    y_disp = Y_DISP
    text_size = TEXT_SIZE
    text_thickness = TEXT_THICKNESS
    for val in [x_disp, y_disp, text_thickness]:
        assert isinstance(val, int), f"{val} is not integer"
    for val in [text_size]:
        assert isinstance(val, float), f"{val} is not flot"

    return vid, srt, out_dir, x_disp, y_disp, text_size, text_thickness

def get_timestamp_from_str(str):
    split = str.split(",")
    hms = split[0].split(":")
    h = int(hms[0])
    m = int(hms[1])
    s = int(hms[2])
    microsecs = int(split[1]) * 1000
    timestamp = h * 3600 + m * 60 + s + microsecs / 1e6
    return timestamp

def parse_srt(filepath):
    assert path.exists(filepath) is True, "SRT file does not exist"
    
    subs = []
    idx = 1
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    symbols = [" ", "\r\n", "\r", ",", ","]
    for i in range(len(lines)):
        line = lines[i].strip()
        if line == str(idx):
            # parse time line
            time_line = lines[i+1].strip()
            times = time_line.split("-->")
            start_time = get_timestamp_from_str(times[0].strip())
            end_time = get_timestamp_from_str(times[1].strip())

            # store subtitle
            j = 2
            
            # get all lines in this time frame
            all_lines = []
            while True:
                sub_line = lines[ i + j ]
                # print("\n\n\nBefore removal", i, f"---{sub_line}---")
                
                k = 0
                while k < len(symbols):
                    symbol = symbols[k]
                    if sub_line.startswith(symbol) or sub_line.endswith(symbol):
                        k = -1
                    # print("symbol: ", k, f"---{symbol}---" , sub_line.startswith(symbol) or sub_line.endswith(symbol), f"---{sub_line}---")
                    sub_line = sub_line.strip(symbol)
                    # print("subline after: ", f"---{sub_line}---")
                    k += 1
                # print("J: ", j, f"---{sub_line}---")
                if sub_line == "" or sub_line == str(idx + 1):
                    break
                # insert info
                j += 1
                all_lines.append(sub_line)

            # divide lines into shorter lines if needed
            if DIVIDE_LINES:
                new_lines = []
                for orig_line in all_lines:
                    words = orig_line.split(" ")
                    if len(words) <= 3:
                        new_lines.append(orig_line)
                    else:
                        divide_ind = len(words) // 2
                        new_lines.append(" ".join(words[:divide_ind]))
                        new_lines.append(" ".join(words[divide_ind:]))
                all_lines = new_lines
            subs.append([line, [start_time, end_time], all_lines])

            # increment idx
            idx += 1
            i += j
    
    return subs

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

def main():

    # get input video info
    cap = cv2.VideoCapture(VIDEO_FILE)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # create output video
    input_file = path.basename(VIDEO_FILE).split(".")[0]
    tmp_output_path = path.join(OUT_DIR, f"tmp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(tmp_output_path, fourcc, fps, (width, height))

    # get subs
    subs = parse_srt(SRT_FILE)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    while cap.isOpened():
        if DEBUG and frame_count >= 1000:
            break
        ret, frame = cap.read()
        if not ret:
            break

        current_time_ms = frame_count / fps
        for i in range(len(subs)):
            sub = subs[-i]
            sub_idx, times, texts = sub
            start_time = times[0] + DELAY_SUB_TIME
            end_time = times[1] + DELAY_SUB_TIME
            
            if start_time <= current_time_ms  and end_time >= current_time_ms:
                draw_subtitle(frame, texts)
                break

        out.write(frame)
        frame_count += 1
        
        # log
        if frame_count % 100 == 0:
            print(f"Wrote {frame_count} out of {total_frames} frames.")

    cap.release()
    out.release()

    # put the audio back in it
    output_path = path.join(OUT_DIR, f"{input_file}_final.mp4")
    os.system(f'ffmpeg -y -i {tmp_output_path} -i {VIDEO_FILE} -c copy -map 0:v:0 -map 1:a:0 {output_path}')

    # remove the temp file
    os.remove(tmp_output_path)
    print("Finished conversion")

if __name__ == "__main__":
    # video_path = "C:\nazim\Projects\Machine Mindset\Youtube\GOT\E1\S09E01_NO_SUB.mp4"
    # srt_path = "C:\nazim\Projects\Machine Mindset\Youtube\GOT\E1\gots9e1.srt"
    # output_path = "C:\nazim\Projects\Machine Mindset\Youtube\GOT\E1\out.mp4"
    # vid_path = "files/rm.mp4"
    # srt_path = "files/captions.srt"
    # out_dir = "files"
    # parse_srt(srt_path)
    process_args()
    main()
