import json
import math
import os
import typing as t
from collections import defaultdict

import docker


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
LEFT_ANKLE = 14
RIGHT_ANKLE = 11


client = docker.from_env()


def run_container(
    image: str,
    command: str,
    working_dir: str,
    volumes: t.Optional[t.Union[list, dict]] = None,
    device_requests: t.Optional[list] = None,
):

    container = client.containers.run(
        image,
        command=command,
        working_dir=working_dir,
        volumes=volumes,
        device_requests=device_requests,
        auto_remove=True,
        detach=True,
        shm_size='512g',
    )

    for log in container.logs(stream=True):
        print(log.decode('utf-8'))


def set_zero_prob_for_keypoint_before_start_line(
    json_path: str,
    start_line: int = 1820,
    verbose: bool = False,
) -> None:

    for filename in os.listdir(json_path):
        if not filename.endswith('.json'):
            continue

        idx = int(filename.split('_')[1])

        with open(os.path.join(json_path, filename), 'r') as f:
            keypoint = json.load(f)

        if len(keypoint['people']) < 1:
            if verbose:
                print(idx, 'no person detected')
            continue

        right_y = keypoint['people'][0]['pose_keypoints_2d'][RIGHT_ANKLE * 3 + 1]
        right_p = keypoint['people'][0]['pose_keypoints_2d'][RIGHT_ANKLE * 3 + 2]
        left_y = keypoint['people'][0]['pose_keypoints_2d'][LEFT_ANKLE * 3 + 1]
        left_p = keypoint['people'][0]['pose_keypoints_2d'][LEFT_ANKLE * 3 + 2]

        if (right_y < start_line and not math.isclose(right_p, 0)) or (left_y < start_line and not math.isclose(left_p, 0)):  # noqa
            if verbose:
                print(idx, 'pass start line')
            continue

        if verbose:
            print(idx, 'before start line and set prob zero')
        keypoint['people'][0]['pose_keypoints_2d'][RIGHT_ANKLE * 3 + 2] = 0
        keypoint['people'][0]['pose_keypoints_2d'][LEFT_ANKLE * 3 + 2] = 0
        with open(os.path.join(json_path, filename), 'w') as f:
            json.dump(keypoint, f)


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
    if inter_width > 0 and inter_height > 0:  # Check if there is an intersection
        intersection_area = inter_width * inter_height
    else:
        intersection_area = 0

    # Calculate union area
    union_area = width1 * height1 + width2 * height2 - intersection_area

    # Calculate Intersection over Union (IoU)
    iou = intersection_area / union_area

    return iou


def load_mot_file(
    mot_file_path: str,
) -> t.Dict[int, t.Dict[int, t.Tuple[int, int, int, int]]]:
    """
    Load a mot file (txt) into a dictionary with a format of
    time (key: int) -> person_id (key: int) -> bbox (value: t.Tuple[int, int, int, int])
    """
    mot_dict = defaultdict(lambda: dict())
    with open(mot_file_path, 'r') as f:
        for line in f:
            t, person_id, left, top, width, height, _, _, _ = line.strip().split(' ')
            t = int(t) - 1  # since it is one indexing
            person_id = int(person_id)
            left = int(left)
            top = int(top)
            width = int(width)
            height = int(height)

            mot_dict[t][person_id] = (left, top, width, height)

    return mot_dict


def find_continuous_personal_bbox(
    frame_num: int,
    mot_dict: t.Dict[int, t.Dict[int, t.Tuple[int, int, int, int]]],
) -> t.Tuple[t.List[int], t.List[t.Tuple[int, int, int, int]]]:
    """
    Load a mot dict and number of frame, find continuous person id and its bbox
    Returns:
        targeted_person_ids (t.List[int]): a list of person_id; person_id = 1 indicates
            there is no suitable person detected
        targeted_person_bboxes (t.List[t.Tuple[int, int, int, int]]]): a list of bbox;
            bbox = () empty tuple indicates there is no suitable person detected
    """
    current_person_id = None
    current_person_bbox = None

    targeted_person_ids = [-1 for _ in range(frame_num)]
    targeted_person_bboxes = [() for _ in range(frame_num)]
    for time_idx in range(frame_num):

        # base case (initially)
        if current_person_id is None:
            if len(mot_dict[time_idx]) == 0:
                continue
            min_distance = VIDEO_WIDTH
            potential_person_id = None
            potential_person_bbox = None
            for person_id, bbox in mot_dict[time_idx].items():
                left, top, width, height = bbox
                bbox_y_center = left + width // 2
                _distance = abs(bbox_y_center - VIDEO_WIDTH // 2)  # bbox center to the center of the video  # noqa
                if _distance < min_distance:
                    min_distance = _distance
                    potential_person_id = person_id
                    potential_person_bbox = bbox

            current_person_id = potential_person_id
            current_person_bbox = bbox

            targeted_person_ids[time_idx] = current_person_id
            targeted_person_bboxes[time_idx] = current_person_bbox

        # after find the first person_id
        else:
            # still has such id -> keep it
            # if current_person_id in mot_dict[time_idx]:
            #     targeted_person_ids[time_idx] = current_person_id

            #     current_person_bbox = mot_dict[time_idx][current_person_id]
            #     targeted_person_bboxes[time_idx] = current_person_bbox

            # # no such id ...
            # else:
            # if there is no bbox detected
            if len(mot_dict[time_idx]) == 0:
                targeted_person_ids[time_idx] = -1
                targeted_person_bboxes[time_idx] = ()
                continue
            # try to find the next person_id
            else:
                max_iou = 0
                potential_person_id = None
                potential_person_bbox = None
                for person_id, bbox in mot_dict[time_idx].items():
                    _iou = calculate_iou(current_person_bbox, bbox)
                    if _iou > max_iou:
                        max_iou = _iou
                        potential_person_id = person_id
                        potential_person_bbox = bbox
                if max_iou < 0.5:
                    targeted_person_ids[time_idx] = -1
                    targeted_person_bboxes[time_idx] = ()
                    continue

                current_person_id = potential_person_id
                current_person_bbox = potential_person_bbox

                targeted_person_ids[time_idx] = current_person_id
                targeted_person_bboxes[time_idx] = current_person_bbox

    return targeted_person_ids, targeted_person_bboxes


def count_json_file(json_path: str) -> int:
    count = 0
    for filename in os.listdir(json_path):
        if not filename.endswith('.json'):
            continue
        count += 1
    return count


def remove_non_target_person(
    json_path: str,
    targeted_person_bboxes: t.List[t.Tuple[int, int, int, int]],
) -> None:
    for filename in os.listdir(json_path):
        if not filename.endswith('.json'):
            continue

        idx = int(filename.split('_')[1])

        with open(os.path.join(json_path, filename), 'r') as f:
            keypoint = json.load(f)

        if len(keypoint['people']) < 1:
            continue

        if len(keypoint['people']) >= 1:
            selected_id = None
            if len(targeted_person_bboxes[idx]) != 0:
                left, top, width, height = targeted_person_bboxes[idx]
                for openpose_people_id in range(len(keypoint['people'])):
                    _keypoint = keypoint['people'][openpose_people_id]['pose_keypoints_2d']
                    right_x = _keypoint[RIGHT_ANKLE * 3 + 0]
                    right_y = _keypoint[RIGHT_ANKLE * 3 + 1]
                    left_x = _keypoint[LEFT_ANKLE * 3 + 0]
                    left_y = _keypoint[LEFT_ANKLE * 3 + 1]

                    if (right_x < left) or (right_x > left + width):
                        continue

                    if (right_y < top) or (right_y > top + height):
                        continue

                    if (left_x < left) or (left_x > left + width):
                        continue

                    if (left_y < top) or (left_y > top + height):
                        continue

                    selected_id = openpose_people_id
                    break
            if selected_id is not None:
                keypoint['people'] = [keypoint['people'][selected_id]]
            else:
                keypoint['people'] = []
            with open(os.path.join(json_path, filename), 'w') as f:
                json.dump(keypoint, f)
