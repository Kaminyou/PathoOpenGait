import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import ndimage
from sklearn.metrics import accuracy_score, jaccard_score, precision_score

from .datasets import GaitTrialInstance
from .metrics import calculate_metrics
from .utils import group_continuous_ones


def get_random_samples(dataset, sample_size=1000):
    n = len(dataset)
    signals = []
    answers = []
    for i in range(sample_size):
        idx = random.randint(0, n - 1)
        signal, answer = dataset[idx]
        signals.append(signal)
        answers.append(answer)
    signals = np.stack(signals) #[:, None, :]  # [B, 1, length]
    answers = np.stack(answers)
    signals = torch.FloatTensor(signals)
    answers = torch.LongTensor(answers)
    return signals, answers


def get_unlabeled_random_samples(unlabeled_dataset, sample_size=1000):
    n = len(unlabeled_dataset)
    signal_u_ws = []
    signal_u_ss = []
    for i in range(sample_size):
        idx = random.randint(0, n - 1)
        (signal_u_w, signal_u_s), _ = unlabeled_dataset[idx]
        signal_u_ws.append(signal_u_w)
        signal_u_ss.append(signal_u_s)
    signal_u_ws = np.stack(signal_u_ws) #[:, None, :]  # [B, 1, length]
    signal_u_ss = np.stack(signal_u_ss)
    signal_u_ws = torch.FloatTensor(signal_u_ws)
    signal_u_ss = torch.FloatTensor(signal_u_ss)
    return (signal_u_ws, signal_u_ss), None



def train(epoch, dataset, model, loss_fn, optimizer, device, iterations=10, writer=None):
    
    train_loss = 0
    model.train()
    
    for i in range(iterations):
        signals, y = get_random_samples(dataset, 256)
        signals = signals.to(device)
        y = y.to(device)
        
        logit = model(signals)
        loss = loss_fn(logit, y)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(f"[{i} / {iterations}] Loss: {loss.item():4f}", end="\r")
        train_loss += loss.item()
        
        pred = torch.argmax(logit, dim=1)
        acc = accuracy_score(y.numpy(), pred.numpy())
    
    train_loss /= iterations
    #writer.add_scalar("Loss/train", train_loss, epoch)
    print(f"Train Avg loss: {train_loss:>8f}   Last Acc={acc:>8f}")
    writer.add_scalar('train_loss', train_loss, epoch)
    writer.add_scalar('train_acc', acc, epoch)


def semi_train(
    epoch,
    labeled_dataset,
    unlabeled_dataet,
    model,
    loss_fn,
    optimizer,
    scheduler,
    device,
    iterations=10,
    threshold=0.95,
    T=1,
    lambda_u=1,
    writer=None,
):
    
    train_loss = 0
    model.train()
    
    for i in range(iterations):
        signals, y = get_random_samples(labeled_dataset, 256)
        signals = signals.to(device)
        y = y.to(device)

        batch_size = signals.shape[0]

        (signals_u_w, signals_u_s), _ = get_unlabeled_random_samples(unlabeled_dataet, 256)
        signals_u_w = signals_u_w.to(device)
        signals_u_s = signals_u_s.to(device)

        inputs = torch.cat((signals, signals_u_w, signals_u_s))
        
        logits = model(inputs)
        logits_x = logits[:batch_size]
        logits_u_w, logits_u_s = logits[batch_size:].chunk(2)
        
        Lx = F.cross_entropy(logits_x, y, reduction='mean')
        pseudo_label = torch.softmax(logits_u_w.detach() / T, dim=-1)
        max_probs, targets_u = torch.max(pseudo_label, dim=-1)
        mask = max_probs.ge(threshold).float()
        # print(mask.sum())

        Lu = (F.cross_entropy(logits_u_s, targets_u,
                                reduction='none') * mask).mean()

        loss = Lx + lambda_u * Lu

        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()
        print(f"[{i} / {iterations}] Loss: {loss.item():4f}", end="\r")
        train_loss += loss.item()
        
        pred = torch.argmax(logits_x, dim=1)
        acc = accuracy_score(y.cpu().numpy(), pred.cpu().numpy())
    
    train_loss /= iterations
    #writer.add_scalar("Loss/train", train_loss, epoch)
    print(f"Train Avg loss: {train_loss:>8f}   Last Acc={acc:>8f}")
    writer.add_scalar('train_loss', train_loss, epoch)
    writer.add_scalar('train_acc', acc, epoch)


def eval_one_instance(gait_instance, model, device='cpu'):
    model.eval()
    with torch.no_grad():
        answers = []
        preds = []
        for signal, answer in gait_instance.generate_all_signal_segments():
            signal = torch.FloatTensor(signal[None, :, :]).to(device)
            logit = model(signal)
            pred = torch.argmax(logit, dim=1)
            preds += list(pred.cpu().numpy())
            answers.append(int(answer))

    acc = accuracy_score(preds, answers)
    #print(f'Acc: {acc:.3f}')
    return acc, signal, answer


def evaluate(epoch, eval_dataset, model, device, prefix='', writer=None):
    accs = []
    for instance in eval_dataset:
        acc, signal, answer = eval_one_instance(instance, model, device)
        accs.append(acc)
    accs = np.array(accs)
    print(f'{prefix + "Acc"}: {accs.mean():.3f} +/- {accs.std():.3f}')
    writer.add_scalar(prefix + 'eval_acc', accs.mean(), epoch)


def integrated_evaluation(epoch, eval_trial_paths, PATIENT_INFO, model, device='cpu', prefix='', writer=None):
    gt_turn_times = []
    pred_turn_times = []
    patient_types = []
    jss = []
    for eval_trial_path in eval_trial_paths:
        gait_instance = GaitTrialInstance(eval_trial_path)
        gait_instance.load_gt(PATIENT_INFO)
        
        model.eval()
        with torch.no_grad():
            answers = []
            preds = []
            probs = []
            for signal, answer in gait_instance.generate_all_signal_segments():
                signal = torch.FloatTensor(signal[None, :, :]).to(device)
                logit = model(signal)
                pred = torch.argmax(logit, dim=1)
                prob = nn.functional.softmax(logit, dim=1)
                preds += list(pred.cpu().numpy())
                answers.append(int(answer))
                probs.append(prob.cpu().numpy()[0, 1])

        acc = accuracy_score(preds, answers)
        js = jaccard_score(preds, answers, average='binary')
        jss.append(js)
        

        preds = np.array(preds)
        answers = np.array(answers)
        probs = np.array(probs)
        

        preds_postprocess = ndimage.binary_erosion(preds, structure=np.ones(10)).astype(preds.dtype)
        preds_postprocess = ndimage.binary_dilation(preds_postprocess, structure=np.ones(10)).astype(preds_postprocess.dtype)

        gt_turn_time = gait_instance.turn_end - gait_instance.turn_start
        try:
            pred_turn_time = group_continuous_ones(preds_postprocess).max()
        except:
            pred_turn_time = 0
        
        gt_turn_times.append(gt_turn_time)
        pred_turn_times.append(pred_turn_time)
        patient_types.append(gait_instance.patient_type)
        
        post_acc = accuracy_score(preds_postprocess, answers)
        # print(f'{gait_instance.patient_type} {gait_instance.trial_id} || Pre-Acc: {acc:.3f} || Post-Acc: {post_acc:.3f} || diff={abs(gt_turn_time-pred_turn_time) * 30 / 1000} s || js={js:.2f}')

    pred_turn_times = np.array(pred_turn_times)
    gt_turn_times = np.array(gt_turn_times)
    patient_types = np.array(patient_types)
    jss = np.array(jss)

    general_metrics = calculate_metrics(pred_turn_times, gt_turn_times, scaling=30/1000)
    print(f'{prefix + "All"} || L1={general_metrics["L1"]:.3f} || MSE={general_metrics["MSE"]:.3f} || Corr={general_metrics["Corr"]:.3f} || Err={general_metrics["Err"]:.3f} || JS={jss.mean():.3f}')
    writer.add_scalar(prefix + 'All-L1', general_metrics["L1"], epoch)
    writer.add_scalar(prefix + 'All-MSE', general_metrics["MSE"], epoch)
    writer.add_scalar(prefix + 'All-Corr', general_metrics["Corr"], epoch)
    writer.add_scalar(prefix + 'All-Err', general_metrics["Err"], epoch)
    writer.add_scalar(prefix + 'All-JS', jss.mean(), epoch)

    group_types = np.unique(patient_types)
    for group_type in group_types:
        # print(group_type)
        predictions_sub = pred_turn_times[patient_types == group_type]
        gts_sub = gt_turn_times[patient_types == group_type]
        groups_sub = patient_types[patient_types == group_type]
        jss_sub = jss[patient_types == group_type]
        sub_metrics = calculate_metrics(predictions_sub, gts_sub, scaling=30/1000)
        print(f'{prefix + group_type} || L1={sub_metrics["L1"]:.3f} || MSE={sub_metrics["MSE"]:.3f} || Corr={sub_metrics["Corr"]:.3f} || Err={sub_metrics["Err"]:.3f} || JS={jss_sub.mean():.3f}')
        
        writer.add_scalar(prefix + group_type + '-L1', sub_metrics["L1"], epoch)
        writer.add_scalar(prefix + group_type + '-MSE', sub_metrics["MSE"], epoch)
        writer.add_scalar(prefix + group_type + '-Corr', sub_metrics["Corr"], epoch)
        writer.add_scalar(prefix + group_type + '-Err', sub_metrics["Err"], epoch)
        writer.add_scalar(prefix + group_type + '-JS', jss_sub.mean(), epoch)
