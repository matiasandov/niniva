import numpy as np
import torch
from torch.compiler import F


@torch.no_grad()
def collect_scores(model, loader, device):
    model.eval()
    scores, labels = [], []
    for x, y in loader:
        x = x.to(device)
        prob = F.softmax(model(x), dim=-1)[:, 1]   # P(wakeword)
        scores.append(prob.cpu().numpy())
        labels.append(y.numpy())
    return np.concatenate(scores), np.concatenate(labels)


def fa_at_miss_rate(scores, labels, target_miss_rate=0.15):
    """False Accepts at a fixed Miss Rate (default 15%)."""
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    # threshold such that miss rate on positives = target
    threshold = np.quantile(pos, target_miss_rate)
    fa = (neg >= threshold).sum()
    return fa, threshold


def det_curve(scores, labels, n_thresholds=200):
    """Returns arrays of (false_detection_rate, miss_rate) for plotting DET."""
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    ths = np.linspace(0, 1, n_thresholds)
    miss = np.array([(pos < t).mean() for t in ths])
    fdr  = np.array([(neg >= t).mean() for t in ths])
    return fdr, miss