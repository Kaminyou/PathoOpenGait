# Algorithms
This document explain details of supported algorithm

## `gait_basic`
This algorithm is the official implementation of our paper.

### Data conversion
To convert 3D trajetories from other cameras, please prepare a file with the following format:

Each row should be:
```
time (ms), left_y (mm), left_x (mm), left_z (mm), right_y (mm), right_x (mm), right_z (mm), 
```
*N* rows represent your record has *N* timeframe. A header for this file is not required.
**Caution:** Please note that the performance would not be guaranteed in this case!