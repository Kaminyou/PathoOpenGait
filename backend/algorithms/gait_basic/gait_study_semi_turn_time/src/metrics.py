import numpy as np


def mse(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    return np.square(np.subtract(a, b)).mean()

def l1(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    return np.abs(np.subtract(a, b)).mean()


def calculate_metrics(predict_variable, gt_variable, scaling):
    gt_variable = np.array(gt_variable, dtype=float)
    predict_variable = np.array(predict_variable, dtype=float)
    
    gt_variable *= scaling
    predict_variable *= scaling
    
    err_percent = abs(predict_variable - gt_variable) / gt_variable
    err_mean = err_percent.mean()
    corr_coef = np.corrcoef(gt_variable, predict_variable)[0, 1]
    l1_err = l1(predict_variable, gt_variable)
    mse_err = mse(predict_variable, gt_variable)
    return {
        'L1': l1_err,
        'MSE': mse_err,
        'Corr': corr_coef,
        'Err': err_mean,
    }
