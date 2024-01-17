import os
import shutil
import typing as t
import pickle

import docker
import pandas as pd

from .._analyzer import Analyzer
from .gait_study_semi_turn_time.inference import simple_inference
from .utils.make_video import render, new_render
from .utils.track import (run_container, count_json_file, find_continuous_personal_bbox,
                   load_mot_file, remove_non_target_person,
                   set_zero_prob_for_keypoint_before_start_line)


MOUNT = os.environ['MOUNT']
WORK_DIR = '/root/backend'
START_LINE = 1820

def avg(l, r, nl, nr):
    return (l * nl + r * nr) / (nl + nr)


def replace_in_filenames(path, old_string, new_string):
    for root, dirs, files in os.walk(path):
        for file in files:
            if old_string in file:
                new_file = file.replace(old_string, new_string)
                os.rename(os.path.join(root, file), os.path.join(root, new_file))


class BasicGaitAnalyzer(Analyzer):
    def __init__(
        self,
        pretrained_path: str = 'algorithms/gait_basic/gait_study_semi_turn_time/weights/semi_vanilla_v2/epoch_94.pth',
    ):
        self.pretrained_path = pretrained_path

    def run(
        self,
        data_root_dir,  # ='/home/kaminyou/repos/PathoOpenGait/backend/data/test_data/'
        file_id,  # '2021-04-01-1-4'
    ) -> t.List[t.Dict[str, t.Any]]:

        os.makedirs(os.path.join(data_root_dir, 'output'), exist_ok=True)
        os.makedirs(os.path.join(data_root_dir, 'output', '2d'), exist_ok=True)
        os.makedirs(os.path.join(data_root_dir, 'output', '3d'), exist_ok=True)

        source_csv = os.path.join(data_root_dir, 'csv', f'{file_id}.csv')
        source_mp4_folder = os.path.join(data_root_dir, 'video')
        output_csv = os.path.join(data_root_dir, 'output', f'{file_id}.csv')
        output_stride_csv = os.path.join(data_root_dir, 'output', f'{file_id}_stride.csv')
        output_2dkeypoint_folder = os.path.join(data_root_dir, 'output', '2d')
        output_3dkeypoint_folder = os.path.join(data_root_dir, 'output', '3d')
        output_3dkeypoint_path = os.path.join(data_root_dir, 'output', '3d', f'{file_id}.mp4.npy')
        output_raw_turn_time_prediction_path = os.path.join(data_root_dir, 'output', 'tt.pickle')

        if os.path.exists('algorithms/gait_basic/zGait/input/2001-01-01-1/2001-01-01-1-1.csv'):
            os.remove('algorithms/gait_basic/zGait/input/2001-01-01-1/2001-01-01-1-1.csv')
        if os.path.exists('algorithms/gait_basic/zGait/output/2001-01-01-1/'):
            shutil.rmtree('algorithms/gait_basic/zGait/output/2001-01-01-1/')

        try:
            shutil.copyfile(source_csv, 'algorithms/gait_basic/zGait/input/2001-01-01-1/2001-01-01-1-1.csv')
            os.system('cd algorithms/gait_basic/zGait && Rscript gait_batch.R input/20010101.csv')
            shutil.copyfile('algorithms/gait_basic/zGait/output/2001-01-01-1/2001-01-01-1.csv', output_csv)
            shutil.copyfile('algorithms/gait_basic/zGait/output/2001-01-01-1/1_stride/2001-01-01-1-1.csv', output_stride_csv)
        except:
            print('No 3D csv')

        os.system(
            'cd algorithms/gait_basic/VideoPose3D && python3 quick_run.py '
            f'--mp4_video_folder {source_mp4_folder} '
            f'--keypoint_2D_video_folder {output_2dkeypoint_folder} '
            f'--keypoint_3D_video_folder {output_3dkeypoint_folder}'
        )

        tt, raw_tt_prediction = simple_inference(
            pretrained_path=self.pretrained_path,
            path_to_npz=output_3dkeypoint_path,
            return_raw_prediction=True,
        )

        with open(output_raw_turn_time_prediction_path, 'wb') as handle:
            pickle.dump(raw_tt_prediction, handle, protocol=pickle.HIGHEST_PROTOCOL)

        sl = -1
        sw = -1
        st = -1
        cadence = -1
        velocity = -1

        try:
            df = pd.read_csv(output_csv, index_col=0)

            table = df.T['total'].T

            left_n = table['left.size']
            right_n = table['right.size']
            left_sl = table['left.stride.lt.mu']
            right_sl = table['right.stride.lt.mu']
            left_sw = table['left.stride.wt.mu']
            right_sw = table['right.stride.wt.mu']
            left_st = table['left.stride.t.mu']
            right_st = table['right.stride.t.mu']
            #tt = table['turn.t']
            cadence = table['cadence']
            velocity = table['velocity']


            sl = avg(left_sl, right_sl, left_n, right_n)
            sw = avg(left_sw, right_sw, left_n, right_n)
            st = avg(left_st, right_st, left_n, right_n)
            #print(sl, sw, st, cadence, velocity, tt)
        except Exception as e:
            print(e)

        try:
            render(data_root_dir=data_root_dir)
        except Exception as e:
            print(e)

        return [
            {
                'key': 'stride length',
                'value': sl / 10,
                'unit': 'cm',
                'type': 'float',
            },
            {
                'key': 'stride width',
                'value': sw / 10,
                'unit': 'cm',
                'type': 'float',
            },
            {
                'key': 'stride time',
                'value': st / 1000,
                'unit': 's',
                'type': 'float',
            },
            {
                'key': 'velocity',
                'value': velocity,
                'unit': 'm/s',
                'type': 'float',
            },
            {
                'key': 'cadence',
                'value': cadence,
                'unit': '1/min',
                'type': 'float',
            },
            {
                'key': 'turn time',
                'value': tt,
                'unit': 's',
                'type': 'float',
            },
        ]


class SVOGaitAnalyzer(Analyzer):
    def __init__(
        self,
        pretrained_path: str = 'algorithms/gait_basic/gait_study_semi_turn_time/weights/semi_vanilla_v2/epoch_94.pth',
    ):
        self.pretrained_path = pretrained_path

    def run(
        self,
        data_root_dir,  # ='/home/kaminyou/repos/PathoOpenGait/backend/data/test_data/'
        file_id,  # '2021-04-01-1-4'
    ) -> t.List[t.Dict[str, t.Any]]:

        os.makedirs(os.path.join(data_root_dir, 'output'), exist_ok=True)
        os.makedirs(os.path.join(data_root_dir, 'output', '2d'), exist_ok=True)
        os.makedirs(os.path.join(data_root_dir, 'output', '3d'), exist_ok=True)

        # input
        source_svo_path = os.path.join(data_root_dir, 'input', f'{file_id}.svo')
        source_txt_path = os.path.join(data_root_dir, 'input', f'{file_id}.txt')

        # meta output
        meta_avi_path = os.path.join(data_root_dir, 'output', f'{file_id}.avi')
        meta_mp4_path = os.path.join(data_root_dir, 'output', f'{file_id}.mp4')
        meta_keypoints_avi_path = os.path.join(data_root_dir, 'output', f'{file_id}-keypoints.avi')
        meta_json_path = os.path.join(data_root_dir, 'output', f'{file_id}-json/')
        meta_csv_path = os.path.join(data_root_dir, 'output', f'{file_id}.csv')

        # meta output (for non-target person removing)
        meta_mot_path = os.path.join(data_root_dir, 'output', f'{file_id}.mot.txt')
        meta_backup_json_path = os.path.join(data_root_dir, 'output', f'{file_id}-json_backup/')
        meta_rendered_mp4_path = os.path.join(data_root_dir, 'output', f'{file_id}-rendered.mp4')
        meta_targeted_person_bboxes_path = os.path.join(data_root_dir, 'output', f'{file_id}-target_person_bboxes.pickle')

        # output
        # source_csv = os.path.join(data_root_dir, 'csv', f'{file_id}.csv')
        os.makedirs(os.path.join(data_root_dir, 'video'), exist_ok=True)
        source_mp4_folder = os.path.join(data_root_dir, 'video')
        source_mp4_path = os.path.join(data_root_dir, 'video', f'{file_id}.mp4')
        output_csv = os.path.join(data_root_dir, 'output', f'{file_id}.csv')
        output_2dkeypoint_folder = os.path.join(data_root_dir, 'output', '2d')
        output_2dkeypoint_path = os.path.join(data_root_dir, 'output', '2d', f'{file_id}.mp4.npz')
        output_3dkeypoint_folder = os.path.join(data_root_dir, 'output', '3d')
        output_3dkeypoint_path = os.path.join(data_root_dir, 'output', '3d', f'{file_id}.mp4.npy')
        meta_custom_dataset_path = os.path.join(data_root_dir, 'output', f'{file_id}-custom-dataset.npz')
        output_raw_turn_time_prediction_path = os.path.join(data_root_dir, 'output', f'{file_id}-tt.pickle')
        output_shown_mp4_path = os.path.join(data_root_dir, 'output', 'render.mp4')
        output_detectron_mp4_path = os.path.join(data_root_dir, 'output', 'render-detectron.mp4')
        output_gait_folder = os.path.join(data_root_dir, 'output', f'{file_id}-rgait-output/')

        # convert to avi
        run_container(
            image='zed-env:latest',
            command=f'python3 /root/svo_export.py "{source_svo_path}" "{meta_avi_path}" 0',
            volumes={
                MOUNT: {'bind': WORK_DIR, 'mode': 'rw'},
            },
            working_dir=WORK_DIR,
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']]),
            ],
        )

        # avi to mp4 (rotate 90 clockwisely)
        run_container(
            image='zed-env:latest',
            command=f'python3 /root/avi_to_mp4.py --avi-path "{meta_avi_path}" --mp4-path "{meta_mp4_path}"',
            volumes={
                MOUNT: {'bind': WORK_DIR, 'mode': 'rw'},
            },
            working_dir=WORK_DIR,
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']]),
            ],
        )

        # openpose
        run_container(
            image='openpose-env:latest',
            command=(
                f'./build/examples/openpose/openpose.bin '
                f'--video {meta_avi_path} --write-video {meta_keypoints_avi_path} '
                f'--write-json {meta_json_path} --frame_rotate 270 --camera_resolution 1920x1080 '
                f'--display 0'
            ),
            volumes={
                MOUNT: {'bind': WORK_DIR, 'mode': 'rw'},
            },
            working_dir='/openpose',
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']]),
            ],
        )

        # tracking
        run_container(
            image='tracking-env:latest',
            command=(
                f'python3 /root/track.py '
                f'--source "{meta_mp4_path}" '
                f'--yolo-model yolov8s.pt '
                f'--classes 0 --tracking-method deepocsort '
                f'--reid-model clip_market1501.pt '
                f'--save-mot --save-mot-path {meta_mot_path} --device cuda:0'
            ),
            volumes={
                MOUNT: {'bind': WORK_DIR, 'mode': 'rw'},
            },
            working_dir='/root',  # sync with the dry run during the building phase
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']]),
            ],
        )
        shutil.copytree(meta_json_path, meta_backup_json_path, dirs_exist_ok=True)
        mot_dict = load_mot_file(meta_mot_path)
        count = count_json_file(meta_json_path)
        targeted_person_ids, targeted_person_bboxes = find_continuous_personal_bbox(count, mot_dict)

        with open(meta_targeted_person_bboxes_path, 'wb') as handle:
            pickle.dump(targeted_person_bboxes, handle, protocol=pickle.HIGHEST_PROTOCOL)

        remove_non_target_person(meta_json_path, targeted_person_bboxes)

        # only allow after start line
        set_zero_prob_for_keypoint_before_start_line(
            json_path=meta_json_path,
            start_line=START_LINE,
        )

        # render_removed_result
        run_container(
            image='zed-env:latest',
            command=(
                f'python3 /root/result_render.py --mp4-path "{meta_mp4_path}" '
                f'--json-path "{meta_json_path}" '
                f'--targeted-person-bboxes-path "{meta_targeted_person_bboxes_path}" '
                f'--rendered-mp4-path "{meta_rendered_mp4_path}"'
            ),
            volumes={
                MOUNT: {'bind': WORK_DIR, 'mode': 'rw'},
            },
            working_dir=WORK_DIR,
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']]),
            ],
        )

        # get xyz
        run_container(
            image='zed-env:latest',
            command=(
                f'/root/depth-sensing/cpp/build/ZED_Depth_Sensing '
                f'{meta_json_path} {source_txt_path} {source_svo_path} {meta_csv_path}'
            ),
            volumes={
                MOUNT: {'bind': WORK_DIR, 'mode': 'rw'},
            },
            working_dir=WORK_DIR,
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']]),
            ],
        )

        # old pipeline
        shutil.copyfile(meta_mp4_path, source_mp4_path)

        if os.path.exists('algorithms/gait_basic/zGait/input/2001-01-01-1/2001-01-01-1-1.csv'):
            os.remove('algorithms/gait_basic/zGait/input/2001-01-01-1/2001-01-01-1-1.csv')
        if os.path.exists('algorithms/gait_basic/zGait/output/2001-01-01-1/'):
            shutil.rmtree('algorithms/gait_basic/zGait/output/2001-01-01-1/')

        try:
            shutil.copyfile(meta_csv_path, 'algorithms/gait_basic/zGait/input/2001-01-01-1/2001-01-01-1-1.csv')
            os.system('cd algorithms/gait_basic/zGait && Rscript gait_batch.R input/20010101.csv')
            shutil.copytree('algorithms/gait_basic/zGait/output/2001-01-01-1/', output_gait_folder)
            replace_in_filenames(output_gait_folder, '2001-01-01-1', file_id)
            shutil.copyfile('algorithms/gait_basic/zGait/output/2001-01-01-1/2001-01-01-1.csv', output_csv)
        except:
            print('No 3D csv')

        os.system(
            'cd algorithms/gait_basic/VideoPose3D && python3 quick_run.py '
            f'--mp4_video_folder "{source_mp4_folder}" '
            f'--keypoint_2D_video_folder "{output_2dkeypoint_folder}" '
            f'--keypoint_3D_video_folder "{output_3dkeypoint_folder}" '
            f'--targeted-person-bboxes-path "{meta_targeted_person_bboxes_path}" '
            f'--custom-dataset-path "{meta_custom_dataset_path}"'
        )

        tt, raw_tt_prediction = simple_inference(
            pretrained_path=self.pretrained_path,
            path_to_npz=output_3dkeypoint_path,
            return_raw_prediction=True,
        )

        with open(output_raw_turn_time_prediction_path, 'wb') as handle:
            pickle.dump(raw_tt_prediction, handle, protocol=pickle.HIGHEST_PROTOCOL)

        sl = -1
        sw = -1
        st = -1
        cadence = -1
        velocity = -1

        try:
            df = pd.read_csv(output_csv, index_col=0)

            table = df.T['total'].T

            left_n = table['left.size']
            right_n = table['right.size']
            left_sl = table['left.stride.lt.mu']
            right_sl = table['right.stride.lt.mu']
            left_sw = table['left.stride.wt.mu']
            right_sw = table['right.stride.wt.mu']
            left_st = table['left.stride.t.mu']
            right_st = table['right.stride.t.mu']
            #tt = table['turn.t']
            cadence = table['cadence']
            velocity = table['velocity']


            sl = avg(left_sl, right_sl, left_n, right_n)
            sw = avg(left_sw, right_sw, left_n, right_n)
            st = avg(left_st, right_st, left_n, right_n)
            #print(sl, sw, st, cadence, velocity, tt)
        except Exception as e:
            print(e)

        try:
            # (openpose + box) + turning; (openpose + box) is on video_path
            new_render(
                video_path=meta_rendered_mp4_path,
                detectron_custom_dataset_path=meta_custom_dataset_path,
                tt_pickle_path=output_raw_turn_time_prediction_path,
                output_video_path=output_shown_mp4_path,
                draw_keypoint=False
            )
            # detectron + turing; draw detectron by meta_custom_dataset_path
            new_render(
                video_path=source_mp4_path,
                detectron_custom_dataset_path=meta_custom_dataset_path,
                tt_pickle_path=output_raw_turn_time_prediction_path,
                output_video_path=output_detectron_mp4_path,
                draw_keypoint=True,
            )
        except Exception as e:
            print('render vidso error:', e)

        return [
            {
                'key': 'stride length',
                'value': sl / 10,
                'unit': 'cm',
                'type': 'float',
            },
            {
                'key': 'stride width',
                'value': sw / 10,
                'unit': 'cm',
                'type': 'float',
            },
            {
                'key': 'stride time',
                'value': st / 1000,
                'unit': 's',
                'type': 'float',
            },
            {
                'key': 'velocity',
                'value': velocity,
                'unit': 'm/s',
                'type': 'float',
            },
            {
                'key': 'cadence',
                'value': cadence,
                'unit': '1/min',
                'type': 'float',
            },
            {
                'key': 'turn time',
                'value': tt,
                'unit': 's',
                'type': 'float',
            },
        ]
