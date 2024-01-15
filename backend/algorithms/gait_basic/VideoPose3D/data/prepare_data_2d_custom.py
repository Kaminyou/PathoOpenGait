# Copyright (c) 2018-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import argparse
import os
import pickle
import sys
import typing as t
from glob import glob

import numpy as np
from data_utils import suggest_metadata


output_prefix_2d = 'data_2d_custom_'

def calculate_iou(
    bbox1: t.Tuple[int, int, int, int],
    bbox2: t.Tuple[int, int, int, int],
) -> float:
    """
    Calculate IOU of two bbox; each bbox in a format of (left, top, width, height)
    """
    # Unpack the bounding boxes
    left1, top1, width1, height1 = bbox1
    left2, top2, width2, height2 = bbox2

    # Calculate the bottom-right corners
    right1, bottom1 = left1 + width1, top1 + height1
    right2, bottom2 = left2 + width2, top2 + height2

    # Calculate intersection coordinates
    inter_left = max(left1, left2)
    inter_top = max(top1, top2)
    inter_right = min(right1, right2)
    inter_bottom = min(bottom1, bottom2)

    # Calculate intersection area
    inter_width = inter_right - inter_left
    inter_height = inter_bottom - inter_top
    if inter_width > 0 and inter_height > 0: # Check if there is an intersection
        intersection_area = inter_width * inter_height
    else:
        intersection_area = 0

    # Calculate union area
    union_area = width1 * height1 + width2 * height2 - intersection_area

    # Calculate Intersection over Union (IoU)
    iou = intersection_area / union_area

    return iou


def decode(filename, targeted_person_bboxes = None):
    # Latin1 encoding because Detectron runs on Python 2.7
    print('Processing {}'.format(filename))
    data = np.load(filename, encoding='latin1', allow_pickle=True)
    bb = data['boxes']
    kp = data['keypoints']
    metadata = data['metadata'].item()
    results_bb = []
    results_kp = []
    for i in range(len(bb)):
        if len(bb[i][1]) == 0 or len(kp[i][1]) == 0:
            # No bbox/keypoints detected for this frame -> will be interpolated
            results_bb.append(np.full(4, np.nan, dtype=np.float32)) # 4 bounding box coordinates
            results_kp.append(np.full((17, 4), np.nan, dtype=np.float32)) # 17 COCO keypoints
            continue
        if targeted_person_bboxes is None:
            best_match = np.argmax(bb[i][1][:, 4])
            best_bb = bb[i][1][best_match, :4]
            best_kp = kp[i][1][best_match].T.copy()
            results_bb.append(best_bb)
            results_kp.append(best_kp)
        else:
            if len(targeted_person_bboxes[i]) == 0:
                results_bb.append(np.full(4, np.nan, dtype=np.float32)) # 4 bounding box coordinates
                results_kp.append(np.full((17, 4), np.nan, dtype=np.float32)) # 17 COCO keypoints
            else:
                max_iou = 0
                potential_box_idx = None
                target_box = targeted_person_bboxes[i]
                for available_box_idx, available_box in enumerate(bb[i][1]):
                    _left, _top, _right, _bottom, _ = available_box
                    _available_bbox = (_left, _top, _right - _left, _bottom - _top)
                    _iou = calculate_iou(target_box, _available_bbox)
                    if _iou > max_iou:
                        max_iou = _iou
                        potential_box_idx = available_box_idx
                if max_iou < 0.5 or potential_box_idx is None:
                    results_bb.append(np.full(4, np.nan, dtype=np.float32)) # 4 bounding box coordinates
                    results_kp.append(np.full((17, 4), np.nan, dtype=np.float32)) # 17 COCO keypoints
                else:
                    best_match = potential_box_idx
                    best_bb = bb[i][1][best_match, :4]
                    best_kp = kp[i][1][best_match].T.copy()
                    results_bb.append(best_bb)
                    results_kp.append(best_kp)

    bb = np.array(results_bb, dtype=np.float32)
    kp = np.array(results_kp, dtype=np.float32)
    kp = kp[:, :, :2] # Extract (x, y)
    
    # Fix missing bboxes/keypoints by linear interpolation
    mask = ~np.isnan(bb[:, 0])
    indices = np.arange(len(bb))
    for i in range(4):
        bb[:, i] = np.interp(indices, indices[mask], bb[mask, i])
    for i in range(17):
        for j in range(2):
            kp[:, i, j] = np.interp(indices, indices[mask], kp[mask, i, j])
    
    print('{} total frames processed'.format(len(bb)))
    print('{} frames were interpolated'.format(np.sum(~mask)))
    print('----------')
    
    return [{
        'start_frame': 0, # Inclusive
        'end_frame': len(kp), # Exclusive
        'bounding_boxes': bb,
        'keypoints': kp,
    }], metadata


if __name__ == '__main__':
    if os.path.basename(os.getcwd()) != 'data':
        print('This script must be launched from the "data" directory')
        exit(0)
        
    parser = argparse.ArgumentParser(description='Custom dataset creator')
    parser.add_argument('-i', '--input', type=str, default='', metavar='PATH', help='detections directory')
    parser.add_argument('-o', '--output', type=str, default='', metavar='PATH', help='output suffix for 2D detections')
    parser.add_argument('--targeted-person-bboxes-path', type=str, default='', help='targeted person bboxes path')
    parser.add_argument('--custom-dataset-path', type=str, default='')
    args = parser.parse_args()
    
    if not args.input:
        print('Please specify the input directory')
        exit(0)
        
    if not args.output:
        print('Please specify an output suffix (e.g. detectron_pt_coco)')
        exit(0)
    
    print('Parsing 2D detections from', args.input)
    
    metadata = suggest_metadata('coco')
    metadata['video_metadata'] = {}
    
    output = {}
    file_list = glob(args.input + '/*.npz')

    targeted_person_bboxes = None
    if args.targeted_person_bboxes_path != '':
        if len(file_list) > 1:
            raise ValueError('When mot_path is used, only one npz is allowed')
        with open(args.targeted_person_bboxes_path, 'rb') as handle:
            targeted_person_bboxes = pickle.load(handle)

    for f in file_list:
        canonical_name = os.path.splitext(os.path.basename(f))[0]
        data, video_metadata = decode(f, targeted_person_bboxes=targeted_person_bboxes)
        output[canonical_name] = {}
        output[canonical_name]['custom'] = [data[0]['keypoints'].astype('float32')]
        metadata['video_metadata'][canonical_name] = video_metadata

    print('Saving...')
    if args.custom_dataset_path != '':
        np.savez_compressed(args.custom_dataset_path, positions_2d=output, metadata=metadata)
    else:
        np.savez_compressed(output_prefix_2d + args.output, positions_2d=output, metadata=metadata)
    print('Done.')