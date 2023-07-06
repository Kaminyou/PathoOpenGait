import os

import torch
from data.combined_patient_info import PATIENT_INFO
from splits.semi_no_label import semi_train_trial_paths
from splits.site_1_train import site_1_train_trial_paths
from splits.site_1_v2 import site_1_eval_trial_paths
from splits.site_2_v1 import site_2_eval_trial_paths
from src.datasets import GaitTrialInstance, SignalDataset, SignalSSLDataset
from src.models import SignalNet
from src.processes import evaluate, integrated_evaluation, semi_train
from src.utils import get_cosine_schedule_with_warmup
from torch.utils.tensorboard import SummaryWriter


if __name__ == '__main__':
    # CONFIG
    # TODO: yaml
    experiment_name = 'semi_vanilla_v3_random_std'
    train_trial_paths = site_1_train_trial_paths
    unlabeled_train_trial_paths = semi_train_trial_paths
    pretrained = None
    device = 'cuda:0'
    epoches = 120

    # Create folder
    log_path = os.path.join('./logs/', experiment_name)
    weight_path = os.path.join('./weights/', experiment_name)
    os.makedirs(log_path, exist_ok=False)
    os.makedirs(weight_path, exist_ok=False)
    writer = SummaryWriter(log_path)

    # DON'T MODIFY
    labeled_train_dataset = SignalDataset(train_trial_paths)
    unlabeled_train_dataset = SignalSSLDataset(semi_train_trial_paths)
    
    site_1_test_dataset = []
    for eval_trial_path in site_1_eval_trial_paths:
        instance = GaitTrialInstance(eval_trial_path)
        instance.load_gt(PATIENT_INFO)
        site_1_test_dataset.append(instance)
    
    site_2_test_dataset = []
    for eval_trial_path in site_2_eval_trial_paths:
        instance = GaitTrialInstance(eval_trial_path)
        instance.load_gt(PATIENT_INFO)
        site_2_test_dataset.append(instance)

    model = SignalNet(num_of_class=2)
    if pretrained is not None:
        model.load_state_dict(torch.load(pretrained))

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.01,
        momentum=0.9,
    )

    scheduler = get_cosine_schedule_with_warmup(
        optimizer, 0, epoches,
    )

    loss_fn = torch.nn.CrossEntropyLoss()
    model.to(device)
    for epoch in range(epoches):
        print(f'=== Epoch {epoch} ===')
        
        semi_train(
            epoch,
            labeled_train_dataset,
            unlabeled_train_dataset,
            model,
            loss_fn,
            optimizer,
            scheduler,
            device=device,
            iterations=100,
            writer=writer,
        )
        evaluate(epoch, site_1_test_dataset, model, device=device, prefix='site1-', writer=writer)
        evaluate(epoch, site_2_test_dataset, model, device=device, prefix='site2-', writer=writer)
        integrated_evaluation(epoch, site_1_eval_trial_paths, PATIENT_INFO, model, device=device, prefix='site1-', writer=writer)
        integrated_evaluation(epoch, site_2_eval_trial_paths, PATIENT_INFO, model, device=device, prefix='site2-', writer=writer)
        # model.to('cpu')
        torch.save(model.state_dict(), os.path.join(weight_path, f'epoch_{epoch}.pth'))
        # model.to(device)