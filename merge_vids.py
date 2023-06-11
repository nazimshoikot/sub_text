import os

import cv2
import numpy as np

from vid_merge_config import VID_1, VID_2, VID_3, VID_4, OUTPUT_PATH, IS_SHORT, VID_LEN, FPS

def stack_videos(videos, grid=(2, 2), output='output.mp4', fps=30.0, frame_size=(480, 640)):
    # Ensure there are enough videos for the grid
    assert len(videos) == grid[0] * grid[1], "Number of videos does not match the grid size"

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output, fourcc, fps, (frame_size[1]*grid[1], frame_size[0]*grid[0]))

    # Create VideoCapture objects for each video
    caps = [cv2.VideoCapture(video) for video in videos]

    frame_num = 0
    last_frames = []
    while True:
        # Read a frame from each video
        frames = [cap.read() for cap in caps]

        # If any frame was not read successfully, then we've reached the end
        incomplete_frame_count = 0
        for i, frame in enumerate(frames):
            if not frame[0]:
                frames[i] = last_frames[i]
                incomplete_frame_count += 1
        if incomplete_frame_count >= len(frames):
            duration = frame_num / fps
            if duration >= VID_LEN:
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
        stack_videos([VID_3, VID_4], grid=(2, 1), output=OUTPUT_PATH, fps=FPS, frame_size=(768, 768))
    else:
        # stack 4 videos
        stack_videos([VID_1, VID_2, VID_3, VID_4], grid=(2, 2), output=OUTPUT_PATH, fps=FPS, frame_size=(768, 768))

