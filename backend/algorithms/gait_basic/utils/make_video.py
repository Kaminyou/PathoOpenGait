import pickle
import typing as t

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter


def get_frames(video_path: str):
    video = cv2.VideoCapture(video_path)
    while True:
        ret, frame = video.read()
        if not ret:
            break
        yield frame
    video.release()


def render(data_root_dir: str):
    video_path = f'{data_root_dir}/video/uploaded.mp4'
    csv_path = f'{data_root_dir}/output/uploaded_stride.csv'
    raw_csv_path = f'{data_root_dir}/csv/uploaded.csv'
    keypoint_path = f'{data_root_dir}/output/2d/uploaded.mp4.npz'
    tt_pickle_path = f'{data_root_dir}/output/tt.pickle'
    output_video_path = f'{data_root_dir}/output/render.mp4'

    with open(tt_pickle_path, 'rb') as handle:
        raw_tt = pickle.load(handle)

    df = pd.read_csv(csv_path, header=0)
    raw_df = pd.read_csv(raw_csv_path, names=["time", "left.y", "left.x", "left.dt", "right.y", "right.x", "right.dt"])

    segmentations = raw_df[['time']].join(df[['time', 'step.leg']], lsuffix='time', rsuffix='time').fillna('-')['step.leg'].values

    kepoints = np.load(keypoint_path, allow_pickle=True)

    frames = []
    for frame in get_frames(video_path):
        frames.append(frame)

    # frame_id = 300

    image_height, image_width, _ = frames[0].shape
    dpi = 300
    writer = FFMpegWriter(fps=30)

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(image_width / dpi, image_height / dpi))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)


    n = len(kepoints.f.keypoints)
    with writer.saving(fig, output_video_path, dpi=dpi):
        for frame_id in range(n):
            ax.clear()
    
            ax.imshow(frames[frame_id][:, :, ::-1])
            xx = kepoints.f.keypoints[frame_id][1].reshape(-1, 17)[0, :]
            yy = kepoints.f.keypoints[frame_id][1].reshape(-1, 17)[1, :]
            ax.scatter(
                x=xx,
                y=yy,
                s=15,
                color='crimson')
            ax.plot([xx[10], xx[8], xx[6], xx[5], xx[7], xx[9]], [yy[10], yy[8], yy[6], yy[5], yy[7], yy[9]], color='crimson')
            ax.plot([xx[6], xx[12], xx[14], xx[16]], [yy[6], yy[12], yy[14], yy[16]], color='crimson')
            ax.plot([xx[5], xx[11], xx[13], xx[15]], [yy[5], yy[11], yy[13], yy[15]], color='crimson')
            ax.plot([xx[12], xx[11]], [yy[12], yy[11]], color='crimson')
            
            # Annotate the current frame type
            #current_frame_type = segmentations[frame_id]
            # if current_frame_type == '-':
            #     current_frame_type = 'none'
            current_frame_type = 'walking'
            if raw_tt[frame_id] == 1:
                current_frame_type = 'turning'
            ax.annotate(current_frame_type, (100, 200), color='white', bbox=dict(facecolor='crimson', edgecolor='black'))

            ax.axis('off')

            writer.grab_frame()


def gen_pairs(l: t.List[int]):
    pairs = [(l[i], l[i + 1]) for i in range(len(l) - 1)]
    return pairs


def new_render(
    video_path: str,
    detectron_custom_dataset_path: str,  # custom data
    tt_pickle_path: str,
    output_video_path: str,
    draw_keypoint: bool = False,
) -> None:

    with open(tt_pickle_path, 'rb') as handle:
        raw_tt = pickle.load(handle)

    detectron_custom_dataset = np.load(detectron_custom_dataset_path, allow_pickle=True)
    keys = list(detectron_custom_dataset.f.positions_2d.item().keys())
    if len(keys) != 1:
        raise ValueError(f'Custom dataset has multiple keys: {keys}')
    key = keys[0]
    keypoints = detectron_custom_dataset.f.positions_2d.item()[key]['custom'][0]

    frames = []
    for frame in get_frames(video_path):
        frames.append(frame)

    image_height, image_width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (image_width, image_height))

    n = len(keypoints)
    for frame_id in range(n):
        frame = frames[frame_id]
        if draw_keypoint:
            for point in keypoints[frame_id]:
                cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 0, 255), -1)  # red color
            
            for (from_idx, to_idx) in gen_pairs([10, 8, 6, 5, 7, 9]):
                cv2.line(frame, tuple(keypoints[frame_id][from_idx].astype(int)), tuple(keypoints[frame_id][to_idx].astype(int)), (0, 0, 255), 5)

            for (from_idx, to_idx) in gen_pairs([6, 12 ,14, 16]):
                cv2.line(frame, tuple(keypoints[frame_id][from_idx].astype(int)), tuple(keypoints[frame_id][to_idx].astype(int)), (0, 0, 255), 5)
            
            for (from_idx, to_idx) in gen_pairs([5, 11 ,13 ,15]):
                cv2.line(frame, tuple(keypoints[frame_id][from_idx].astype(int)), tuple(keypoints[frame_id][to_idx].astype(int)), (0, 0, 255), 5)
            
            for (from_idx, to_idx) in gen_pairs([12, 11]):
                cv2.line(frame, tuple(keypoints[frame_id][from_idx].astype(int)), tuple(keypoints[frame_id][to_idx].astype(int)), (0, 0, 255), 5)
        
        current_frame_type = 'walking'
        if raw_tt[frame_id] == 1:
            current_frame_type = 'turning'
        
        # add white text on a red rectangle
        text = current_frame_type
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_thickness = 3
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_width, text_height = text_size
        margin = 5
        lower_left_corner = (100, 200 - text_height - margin)
        upper_right_corner = (100 + text_width + margin, 200 + margin)
        cv2.rectangle(frame, lower_left_corner, upper_right_corner, (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, text, (100, 200), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        out.write(frame)
