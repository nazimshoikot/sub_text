from os import path
from datetime import datetime

import cv2
import pysrt

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
    with open(filepath) as f:
        lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i].strip()
        if line == str(idx):
            # parse time line
            time_line = lines[i+1].strip()
            times = time_line.split("-->")
            start_time = get_timestamp_from_str(times[0].strip())
            end_time = get_timestamp_from_str(times[1].strip())

            # store subtitle
            sub_line = lines[i+2].strip()

            # insert info
            subs.append([line, [start_time, end_time], sub_line])

            # increment idx
            idx += 1
            i += 2
    
    return subs

def draw_subtitle(frame, text, position, font_scale=1.5, font_thickness=2, font_face=cv2.FONT_HERSHEY_SIMPLEX, color=(255, 255, 255)):
    text_size, _ = cv2.getTextSize(text, font_face, font_scale, font_thickness)
    x, y = position
    cv2.rectangle(frame, (x, y - text_size[1]), (x + text_size[0], y + text_size[1] // 2), (0, 0, 0), -1)
    cv2.putText(frame, text, position, font_face, font_scale, color, font_thickness, cv2.LINE_AA)

def main(video_path, srt_path, output_path):
    # get input video info
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # create output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # open subs
    subs = parse_srt(srt_path)
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time_ms = frame_count / fps
        for sub in subs:
            sub_idx, times, text = sub
            start_time = times[0]
            end_time = times[1]
            
            if start_time <= current_time_ms  and end_time >= current_time_ms:
                print("Times: ", start_time, end_time, current_time_ms)
                position = (100, height - 400)
                draw_subtitle(frame, text, position)
                break

        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

if __name__ == "__main__":
    video_path = "rm.mp4"
    srt_path = "captions.srt"
    output_path = "output_video.mp4"
    # parse_srt(srt_path)
    main(video_path, srt_path, output_path)
