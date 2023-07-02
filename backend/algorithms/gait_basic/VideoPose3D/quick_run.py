import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mp4_video_folder',
        default='/home/kaminyou/repos/PathoOpenGait/backend/data/test_data/video',
        help='path to pretrained weight file',
        type=str,
    )
    parser.add_argument(
        '--keypoint_2D_video_folder',
        default=None,
        help='/home/kaminyou/repos/PathoOpenGait/backend/algorithms/gait_basic/VideoPose3D/mydata/keypoint_2d',
        type=str,
    )
    parser.add_argument(
        '--keypoint_3D_video_folder',
        default=None,
        help='/home/kaminyou/repos/PathoOpenGait/backend/algorithms/gait_basic/VideoPose3D/mydata/keypoint_3d/',
        type=str,
    )
    args = parser.parse_args()

    mp4_video_folder = args.mp4_video_folder
    keypoint_2D_video_folder = args.keypoint_2D_video_folder
    keypoint_3D_video_folder = args.keypoint_3D_video_folder

    os.system(f"cd inference && python infer_video_d2.py --cfg COCO-Keypoints/keypoint_rcnn_R_101_FPN_3x.yaml --output-dir {keypoint_2D_video_folder} --image-ext mp4 {mp4_video_folder}")

    os.system(f"cd data && python3 prepare_data_2d_custom.py -i {keypoint_2D_video_folder} -o myvideos")

    num_of_file = len(os.listdir(mp4_video_folder))
    for idx, file in enumerate(os.listdir(mp4_video_folder)):
        print(f"[{idx+1} / {num_of_file}] {file}        ")
        os.system(f"python run.py -d custom -k myvideos -arc 3,3,3,3,3 -c checkpoint --evaluate pretrained_h36m_detectron_coco.bin --render --viz-subject {file} --viz-action custom --viz-camera 0 --viz-video {os.path.join(mp4_video_folder,file)} --viz-export {os.path.join(keypoint_3D_video_folder,file)} --viz-size 6")
