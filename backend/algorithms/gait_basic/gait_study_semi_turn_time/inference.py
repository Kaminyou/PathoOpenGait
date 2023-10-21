import argparse
import typing as t

import numpy as np
import torch
import torch.nn as nn
from scipy import ndimage

from .src.datasets import GaitTrialInstanceSimple
from .src.models import SignalNet
from .src.utils import group_continuous_ones


def signal_verifier(signal):
    return np.any(np.isnan(signal))


def simple_inference(
    pretrained_path: str,
    path_to_npz: str,
    return_raw_prediction: bool = False,
) -> t.Union[float, t.Tuple[float, t.List[bool]]]:
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
            if signal_verifier(signal):
                return -1
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

    if return_raw_prediction:
        return pred_turn_time * 30 / 1000, list(preds_postprocess)
    else:
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
