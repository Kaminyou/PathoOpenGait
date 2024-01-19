# Algorithms
This document explain details of supported algorithm

## `BasicGaitAnalyzer` in `gait_basic`
This algorithm is the official implementation of our paper.

### Data conversion
To convert 3D trajetories from other cameras, please prepare a file with the following format:

Each row should be:
```
time (ms), left_y (mm), left_x (mm), left_z (mm), right_y (mm), right_x (mm), right_z (mm), 
```
*N* rows represent your record has *N* timeframe. A header for this file is not required.
**Caution:** Please note that the performance would not be guaranteed in this case!

## `SVOGaitAnalyzer` in `gait_basic`
This algorithm enables input of svo and txt output from a ZED camera recording program.
- `.svo`: A 3D video recorded by a ZED camera
- `.txt`: A file indicate the timestamp of each frame of the 3D video. An example is,
```
1,2233193
2,2233213
3,2233248
...
FRAME_ID, ABSOLUTE_TIMESTAMP (in ms)
```
If you don't have such txt, please generate one and support the fps=30

### Output files 
In `./backend/data/UPLOAD_UUID/`
```
.
├── input
│   ├── 2024-01-19-1-6.svo  # uploaded svo
│   └── 2024-01-19-1-6.txt  # uploaded txt
├── out
│   ├── 2024-01-19-1-6.avi  # svo -> avi (left camera without rotation)
│   ├── 2024-01-19-1-6.csv  # file results (gait parameters)
│   ├── 2024-01-19-1-6-raw.csv  # left and right legs' keypoints by time
│   ├── 2024-01-19-1-6-custom-dataset.npz  # single person dectron's keypoints for 3D estimation
│   ├── 2024-01-19-1-6-json/  # openpose output after people removing
│   ├── 2024-01-19-1-6-json_backup/  # original openpose output
│   ├── 2024-01-19-1-6-keypoints.avi  # openpose detection visualization (still multiple person)
│   ├── 2024-01-19-1-6.mot.txt  # a list of bbox to indicate different person in video
│   ├── 2024-01-19-1-6.mp4  # svo -> mp4 (left camera with rotation for turn time estimation)
│   ├── 2024-01-19-1-6-rendered.mp4  # openpose's leg keypoint + person tracking (box) visualization
│   ├── 2024-01-19-1-6-target_person_bboxes.pickle  # bbox to track a targeted person in video
│   ├── 2024-01-19-1-6-tt.pickle  # turn time estimation result
│   ├── 2d/
│   │   └── 2024-01-19-1-6.mp4.npz  # detectron 2D keypoint output
│   ├── 3d/
│   │   └── 2024-01-19-1-6.mp4.npy  # 3D keypoints estimation output
│   ├── render-detectron.mp4  # box + 2D detectron output + turn time visualization
│   ├── render.mp4  # box + openpose's leg + turn time visualization
│   └── zGait/  # zGait output
│       ├── gait_batch.R  # R script to calcuate gait parameters
│       ├── input/
│       │   ├── 20010101.csv  # a helper file
│       │   └── 2024-01-19-1-6/
│       │       └── 2024-01-19-1-6.csv
│       └── output/
│           ├── 2024-01-19-1-6/
│           │   ├── 00_raw/
│           │   │   └── 2024-01-19-1-6.csv
│           │   ├── 0_clean/
│           │   │   └── 2024-01-19-1-6.csv
│           │   ├── 1_stride/
│           │   │   └── 2024-01-19-1-6.csv
│           │   ├── 2024-01-19-1-6.csv
│           │   ├── 2024-01-19-1-6_left.csv
│           │   └── 2024-01-19-1-6_right.csv
│           └── batch_log/
│               └── 20010101.csv
└── video
    └── 2024-01-19-1-6.mp4  # 3D estimation metadata
```