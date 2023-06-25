import os

import cv2
import numpy as np

from configs.vid_merge_config import VID_1, VID_2, VID_3, VID_4, OUTPUT_PATH, IS_SHORT, VID_LEN, FPS, DEBUG, CHANGE_DELAY

def stack_videos(videos_list, grid=(2, 2), output='output.mp4', fps=30.0, frame_size=(480, 640)):
    num_videos = len(videos_list)
    # Ensure there are enough videos for the grid
    assert num_videos == grid[0] * grid[1], "Number of videos does not match the grid size"

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output, fourcc, fps, (frame_size[1]*grid[1], frame_size[0]*grid[0]))

    # Create VideoCapture objects for each video
    caps = []
    cap_i = 0
    while True:
        none_count = 0
        for i in range(num_videos):
            videos = videos_list[i]
            if cap_i < len(videos) and videos[cap_i] is not None:
                caps.append(cv2.VideoCapture(videos[cap_i]))
            else:
                caps.append(None)
                none_count += 1
        cap_i += 1
        if none_count >= num_videos:
            break

    frame_num = 0
    last_frames = []
    num_repeats = [0, 0, 0, 0]
    change_delay_frame_num = CHANGE_DELAY * fps
    while True:
        # print("Reading frames again")
        # Read a frame from each video
        frames = [cap.read() for cap_ind, cap in enumerate(caps) if cap_ind < num_videos]


        # If any frame was not read successfully, then we've reached the end
        incomplete_frame_count = 0
        for i, frame in enumerate(frames):
            if not frame[0]:
                frames[i] = last_frames[i]
                if num_repeats[i] >= change_delay_frame_num:
                    next_cap_ind = i + num_videos
                    while next_cap_ind < len(caps) and caps[next_cap_ind] is not None:
                        caps[next_cap_ind - num_videos] = caps[next_cap_ind]
                        next_cap_ind += num_videos
                    num_repeats[i] = 0
                else:
                    num_repeats[i] += 1
                incomplete_frame_count += 1
        
        if incomplete_frame_count >= len(frames):
            duration = frame_num / fps
            if duration >= VID_LEN or (DEBUG and frame_num >= 900):
                break
        
        last_frames = frames

        # Otherwise, retrieve the frames
        frames = [frame[1] for frame in frames]

        # Reshape the list of frames into the grid
        frames_grid = np.array(frames).reshape(grid + frames[0].shape)

        # Concatenate along the rows, then concatenate the result along columns
        frame = np.concatenate(np.concatenate(frames_grid, axis=1), axis=1)

        # Write the frame
        out.write(frame)

        frame_num += 1
        if frame_num % 100 == 0:
            print(f"Wrote {frame_num} frames.")



    # Release everything
    for cap in caps:
        if cap is not None:
            cap.release()
    out.release()
    print("Finished writing")

def check_arguments():
    for vid_paths in [VID_1, VID_2, VID_3, VID_4]:
        for vid_path in vid_paths:
            assert os.path.exists(vid_path), f"{vid_path} does not exist"

    if IS_SHORT:
        assert VID_LEN <= 59, "Video length too big for short"

if __name__ == "__main__":
    if IS_SHORT:
        # stack 2 videos
        stack_videos([VID_3], grid=(1, 1), output=OUTPUT_PATH, fps=FPS, frame_size=(768, 768))
    else:
        # stack 4 videos
        stack_videos([VID_1, VID_2, VID_3, VID_4], grid=(2, 2), output=OUTPUT_PATH, fps=FPS, frame_size=(768, 768))

