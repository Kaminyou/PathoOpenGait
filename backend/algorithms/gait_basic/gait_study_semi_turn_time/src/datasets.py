import random
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.signal import medfilt
from skimage.restoration import denoise_wavelet
from torch.utils.data import Dataset

from .augmentation import strong_augment, weak_augment
from .patient_info import PATIENT_INFO


class GaitTrialInstance:
    
    def __init__(self, path_to_csv, signal_size=129):
        self.path_to_csv = path_to_csv
        self.parse_id()
        self.path_to_npz = f'gait_video_3d_keypoints/{self.trial_id}.mp4.npy'
        
        self.signals = np.load(self.path_to_npz).reshape(-1, 51)  # L, C
        self.signal_length = self.signals.shape[0]
        
    def parse_id(self):
        self.trial_id = self.path_to_csv.rsplit('/', 1)[1].rsplit('.', 1)[0]
        self.patient_id = self.trial_id.rsplit('-', 1)[0]
        
    def denoise(self, signal):
        return denoise_wavelet(
            signal,
            wavelet='db1',
            mode='soft',
            wavelet_levels=4,
            method='BayesShrink',
            rescale_sigma='True',
        )
    
    def process_signal(self, signal):
        #signal = np.nan_to_num(signal)
        #signal = np.diff(np.nan_to_num(signal))
#         signal = np.nan_to_num(signal)
#         signal[abs(signal) > TOLERATE] = 0
#         signal /= TOLERATE
        return signal
    
    def load_gt(self, gt_dict):
        patient_verfication_info = gt_dict[self.patient_id]
        self.turn_time_points = None
        for verification in patient_verfication_info['verification']:
            if verification['trial_id'] == self.trial_id:
                self.turn_time_points = verification['turns']
                break
        if self.turn_time_points is None:
            raise ValueError
        self.turn_start = self.turn_time_points[0]
        self.turn_end = self.turn_time_points[1]
        self.patient_type = patient_verfication_info['type']
    
    @lru_cache(maxsize=None)
    def pad_signal(self, pad_size):
        return np.pad(self.signals, ((pad_size, pad_size), (0, 0)), mode = 'constant')
        
    
    def crop_signal_from_one_point(self, timestamp, signal_size=129): #  'left_x', 'right_x'
        # signal_size must be odd
        half_size = signal_size // 2
        pad_signal = self.pad_signal(half_size)
        crop_signal = pad_signal[timestamp: timestamp + signal_size, :]
        return crop_signal.T  # L, C -> C, L
    
    def crop_signal_with_answer(self, timestamp, signal_size=129):
        signal = self.crop_signal_from_one_point(timestamp, signal_size=signal_size)
        answer = self.turn_start <= timestamp < self.turn_end
        return signal, answer
    
    def crop_random_signal_with_answer(self, signal_size=129):
        random_idx = random.randint(0, self.signal_length - 1)
        return self.crop_signal_with_answer(random_idx, signal_size=signal_size)
    
    def crop_random_siginal_without_answer(self, signal_size=129):
        random_idx = random.randint(0, self.signal_length - 1)
        return self.crop_signal_from_one_point(random_idx, signal_size=signal_size)
    
    def generate_all_signal_segments(self, signal_size=129):
        for i in range(self.signal_length):
            yield self.crop_signal_with_answer(i, signal_size=signal_size)

    def generate_all_signal_segments_without_answer(self, signal_size=129):
        for i in range(self.signal_length):
            yield self.crop_signal_from_one_point(i, signal_size=signal_size)
            

class GaitTrialInstanceSimple(GaitTrialInstance):
    def __init__(self, trial_id, signal_size=129, path_to_npz=None):
        self.trial_id = trial_id
        self.parse_id()
        if path_to_npz is None:
            self.path_to_npz = f'gait_video_3d_keypoints/{self.trial_id}.mp4.npy'
        else:
            self.path_to_npz = path_to_npz
        
        self.signals = np.load(self.path_to_npz).reshape(-1, 51)  # L, C
        self.signal_length = self.signals.shape[0]
        
    def parse_id(self):
        self.patient_id = self.trial_id.rsplit('-', 1)[0]


class _SignalDataset(Dataset):
    def __init__(
        self,
        trial_paths,
        train_mode=True,
    ):
        self.trial_paths = trial_paths
        self.load_instance()
    
    def load_instance(self):
        self.trial_instances = []
        for trial_path in self.trial_paths:
            instance = GaitTrialInstance(
                path_to_csv=trial_path,
            )
            instance.load_gt(PATIENT_INFO)
            self.trial_instances.append(instance)

    def __len__(self):
        return len(self.trial_instances)


class SignalDataset(_SignalDataset):

    def __getitem__(self, idx):
        instance = self.trial_instances[idx]
        signal, answer = instance.crop_random_signal_with_answer()
        return signal, answer


class SignalSSLDataset(_SignalDataset):

    def load_instance(self):
        self.trial_instances = []
        for trial_path in self.trial_paths:
            instance = GaitTrialInstance(
                path_to_csv=trial_path,
            )
            self.trial_instances.append(instance)

    def __getitem__(self, idx):
        instance = self.trial_instances[idx]
        signal = instance.crop_random_siginal_without_answer()
        signal_s = strong_augment(signal)
        signal_w = weak_augment(signal)

        return (signal_w, signal_s), None
