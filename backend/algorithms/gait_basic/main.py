import os
import shutil
import typing as t
import pickle

import pandas as pd

from .._analyzer import Analyzer
from .gait_study_semi_turn_time.inference import simple_inference
from .utils.make_video import render


def avg(l, r, nl, nr):
    return (l * nl + r * nr) / (nl + nr)


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
