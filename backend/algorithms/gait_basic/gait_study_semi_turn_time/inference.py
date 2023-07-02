import argparse

import numpy as np
import torch
import torch.nn as nn
from scipy import ndimage

from .src.models import SignalNet
from .src.datasets import GaitTrialInstanceSimple

from .src.utils import group_continuous_ones


def simple_inference(pretrained_path: str, path_to_npz: str) -> float:
    # given a npz of 3D tragetories and pretrained_path
    # output the turing time in second

    model = SignalNet(num_of_class=2)
    model.load_state_dict(torch.load(pretrained_path))

    gait_instance = GaitTrialInstanceSimple(
        trial_id='',
        path_to_npz=path_to_npz,
    )
    model.eval()
    with torch.no_grad():
        preds = []
        probs = []
        for signal in gait_instance.generate_all_signal_segments_without_answer():
            signal = torch.FloatTensor(signal[None, :, :])
            logit = model(signal)
            pred = torch.argmax(logit, dim=1)
            prob = nn.functional.softmax(logit, dim=1)
            preds += list(pred.numpy())
            probs.append(prob.numpy()[0, 1])

    preds = np.array(preds)
    probs = np.array(probs)
    preds_postprocess = ndimage.binary_erosion(preds, structure=np.ones(10)).astype(preds.dtype)
    preds_postprocess = ndimage.binary_dilation(preds_postprocess, structure=np.ones(10)).astype(preds_postprocess.dtype)

    try:
        pred_turn_time = group_continuous_ones(preds_postprocess).max()
    except:
        pred_turn_time = 0

    return pred_turn_time * 30 / 1000


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pretrained-path',
        default=None,
        help='path to pretrained weight file',
        type=str,
    )
    parser.add_argument(
        '--npz-file-path',
        default=None,
        help='path to npz file',
        type=str,
    )
    args = parser.parse_args()

    turn_time = simple_inference(
        pretrained_path=args.pretrained_path,
        path_to_npz=args.npz_file_path,
    )
    print(turn_time)
