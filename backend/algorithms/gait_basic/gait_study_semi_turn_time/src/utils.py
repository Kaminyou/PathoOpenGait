import math

import numpy as np
from torch.optim.lr_scheduler import LambdaLR


def group_continuous_ones(array):
    n = len(array)
    lengths = []
    index = 0
    while (index < n):
        if array[index] == 1:
            start = index
            while (index + 1 < n and array[index + 1] == 1):
                index += 1
            length = index - start + 1
            lengths.append(length)
        index += 1
    return np.array(lengths)


def get_cosine_schedule_with_warmup(optimizer,
                                    num_warmup_steps,
                                    num_training_steps,
                                    num_cycles=7./16.,
                                    last_epoch=-1):
    def _lr_lambda(current_step):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        no_progress = float(current_step - num_warmup_steps) / \
            float(max(1, num_training_steps - num_warmup_steps))
        return max(0., math.cos(math.pi * num_cycles * no_progress))

    return LambdaLR(optimizer, _lr_lambda, last_epoch)
