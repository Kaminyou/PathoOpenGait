import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .metrics import l1, mse


def draw_one_variable(predict_variable, gt_variable, title, groups, scaling, unit='ms'):
    gt_variable = np.array(gt_variable, dtype=float)
    predict_variable = np.array(predict_variable, dtype=float)
    
    gt_variable *= scaling
    predict_variable *= scaling
    
    err_percent = abs(predict_variable - gt_variable) / gt_variable
    err_mean = err_percent.mean()
    err_std = err_percent.std()
    
    corr_coef = np.corrcoef(gt_variable, predict_variable)[0, 1]
    l1_err = l1(predict_variable, gt_variable)
    mse_err = mse(predict_variable, gt_variable)
    #plt.scatter(gt_variable, predict_variable)
    df = pd.DataFrame({'gt_variable': gt_variable, 'predict_variable': predict_variable, 'groups': groups})
    #sns.scatterplot(df, x='gt_variable', y='predict_variable', hue='groups')
    sns.scatterplot(x=df.gt_variable, y=df.predict_variable, hue=df.groups)
    
    max_x = max(gt_variable) * 1.1
    max_y = max(predict_variable) * 1.1

    plt.plot([0, max(max_x, max_y)], [0, max(max_x, max_y)], label='y=x', color='red')
    plt.xlim(0, max_x)
    plt.ylim(0, max_y)
    plt.xlabel(f'ground truth ({unit})')
    plt.ylabel(f'prediction ({unit})')
    #plt.title(f'{title} (corr={corr_coef:.3f})')
    plt.title(f'{title} \n L1={l1_err:.3f} {unit} || MSE={mse_err:.3f} {unit}² || corr={corr_coef:.3f} || err={err_mean * 100:.3f}%')
    plt.grid()
    plt.legend()
    plt.show()
    #return df

