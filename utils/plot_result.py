import numpy as np
import matplotlib.pyplot as plt
import json
from os import path


def plot_approach_f1(name: str):
    '''

    :param name: approach name
    '''
    with open(path.join("res", f"{name}.json"), "r") as f:
        res = json.load(f)
        size = len(res)
        x = np.arange(size)
        recall = list()
        precision = list()
        f1 = list()
        total_width, n = 0.6, 3
        width = total_width / n
        x = x - (total_width - width) / 2
        labels = list()
        for project in res:
            labels.append(project)
            recall.append(res[project]["recall"])
            precision.append(res[project]["precision"])
            f1.append(res[project]["f1"])
        plt.xticks(fontsize=10)
        plt.rcParams['figure.figsize']=(18,12)
        plt.bar(x, precision, width=width, label='precision')

        plt.bar(x + width, recall, width=width, label='recall', tick_label=labels)
        plt.bar(x + 2 * width, f1, width=width, label='f1')
        plt.legend()
        out_dir = 'res/plot_png'
        plt.savefig(path.join(out_dir,name+".png"))
        plt.close()
        f.close()

    
