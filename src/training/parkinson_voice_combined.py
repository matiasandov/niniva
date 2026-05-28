"""
PD vs Healthy Classification Pipeline — Tier A features
- Subject-independent nested CV
- Multiple model comparison
- Recording- and subject-level metrics with bootstrap CIs
- Two tracks: Istanbul-only and Istanbul + Oxford-augmented
"""

import os

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                              confusion_matrix, classification_report)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")

RNG = 42

# ---------------------------------------------------------------------
# 1. Load and define Tier A
# ---------------------------------------------------------------------
os.chdir("c:/Users/matts/Desktop/wakeup-ai")

df = pd.read_csv("data\parkinson\combined_parkinson_voice.csv")

TIER_A = ['Jitter(%)','Jitter(Abs)','Jitter:RAP','Jitter:PPQ5','Jitter:DDP',
          'Shimmer','Shimmer(dB)','Shimmer:APQ3','Shimmer:APQ5','Shimmer:APQ11',
          'Shimmer:DDA','NHR','HNR']

# Istanbul-only subset (the only source with both classes)
ist = df[df['source'].str.startswith('istanbul')].copy()
oxf = df[df['source'] == 'oxford'].copy()  # all PD, used for augmentation only

print(f"Istanbul: {len(ist)} recordings, "
      f"{ist['subject_id'].nunique()} subjects, "
      f"class balance: {ist['status'].value_counts().to_dict()}")
print(f"Oxford  : {len(oxf)} recordings, "
      f"{oxf['subject_id'].nunique()} subjects (all PD)")

# ---------------------------------------------------------------------
# 2. Domain-shift sanity check
# ---------------------------------------------------------------------
from sklearn.linear_model import LogisticRegressionCV
src_y = (df['source'] == 'oxford').astype(int).values
src_X = df[TIER_A].fillna(0).values
src_auc = roc_auc_score(
    src_y,
    LogisticRegressionCV(cv=3, max_iter=1000).fit(src_X, src_y).predict_proba(src_X)[:,1]
)
print(f"\n[Diagnostic] Source-detection AUC = {src_auc:.3f} "
      f"(>0.7 indicates strong domain shift)")

# ---------------------------------------------------------------------
# 3. Model zoo with hyperparameter grids (small grids to keep nested CV tractable)
# ---------------------------------------------------------------------
def build_models():
    return {
        'LogReg': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', LogisticRegression(max_iter=2000, class_weight='balanced'))]),
            {'clf__C': [0.1, 1.0, 10.0]}
        ),
        'SVM-RBF': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', SVC(kernel='rbf', probability=True,
                                  class_weight='balanced', random_state=RNG))]),
            {'clf__C': [0.5, 1, 5], 'clf__gamma': ['scale', 0.1]}
        ),
        'RandomForest': (
            RandomForestClassifier(class_weight='balanced',
                                   random_state=RNG, n_jobs=-1),
            {'n_estimators': [300, 600], 'max_depth': [None, 8],
             'min_samples_leaf': [1, 3]}
        ),
        'XGBoost': (
            XGBClassifier(eval_metric='logloss', random_state=RNG,
                          n_jobs=-1, verbosity=0),
            {'n_estimators': [300], 'max_depth': [4, 6],
             'learning_rate': [0.05, 0.1], 'subsample': [0.8]}
        ),
        'LightGBM': (
            LGBMClassifier(class_weight='balanced', random_state=RNG,
                           n_jobs=-1, verbosity=-1),
            {'n_estimators': [300], 'num_leaves': [15, 31],
             'learning_rate': [0.05, 0.1]}
        ),
    }

# ---------------------------------------------------------------------
# 4. Subject-level aggregation
# ---------------------------------------------------------------------
def subject_level_metrics(subject_ids, y_true_rec, y_prob_rec, threshold=0.5):
    """Aggregate per-recording predictions to per-subject via mean probability."""
    out = (pd.DataFrame({'sid': subject_ids, 'y': y_true_rec, 'p': y_prob_rec})
             .groupby('sid')
             .agg(y=('y', 'first'), p=('p', 'mean'))
             .reset_index())
    out['pred'] = (out['p'] >= threshold).astype(int)
    return out

def bootstrap_ci(values, n_boot=1000, alpha=0.05):
    rng = np.random.default_rng(RNG)
    boots = [np.mean(rng.choice(values, size=len(values), replace=True))
             for _ in range(n_boot)]
    return np.percentile(boots, [100*alpha/2, 100*(1-alpha/2)])

# ---------------------------------------------------------------------
# 5. Nested CV runner
# ---------------------------------------------------------------------
def nested_cv(X, y, groups, model_name, estimator, param_grid,
              augment_X=None, augment_y=None, augment_groups=None,
              augment_weight=0.3):
    """
    Outer GroupKFold(5) for unbiased eval.
    Inner GroupKFold(3) for hyperparam tuning.
    If augment_* provided, add those rows ONLY to the training fold.
    """
    outer = GroupKFold(n_splits=5)
    inner = GroupKFold(n_splits=3)

    rec_preds = []   # store per-recording results for later subject-level aggregation
    fold_subj_acc = []
    fold_subj_auc = []
    fold_subj_f1  = []

    for fold, (tr_idx, te_idx) in enumerate(outer.split(X, y, groups=groups)):
        X_tr, X_te = X[tr_idx], X[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]
        g_tr       = groups[tr_idx]
        g_te       = groups[te_idx]

        # ---- optional augmentation (training fold only) ----
        sample_weight = np.ones(len(y_tr))
        if augment_X is not None:
            X_tr = np.vstack([X_tr, augment_X])
            y_tr = np.concatenate([y_tr, augment_y])
            g_tr = np.concatenate([g_tr, augment_groups])
            sample_weight = np.concatenate(
                [sample_weight, np.full(len(augment_y), augment_weight)]
            )

        # ---- inner CV for hyperparameter tuning ----
        gs = GridSearchCV(
            estimator, param_grid,
            cv=list(inner.split(X_tr, y_tr, groups=g_tr)),
            scoring='roc_auc', n_jobs=-1, refit=True
        )
        # XGBoost/LightGBM accept sample_weight via fit_params; others ignore
        try:
            gs.fit(X_tr, y_tr, sample_weight=sample_weight)
        except (TypeError, ValueError):
            gs.fit(X_tr, y_tr)

        best = gs.best_estimator_
        p_te = best.predict_proba(X_te)[:, 1]

        # ---- subject-level metrics for this fold ----
        sub = subject_level_metrics(g_te, y_te, p_te)
        fold_subj_acc.append(accuracy_score(sub['y'], sub['pred']))
        fold_subj_f1.append(f1_score(sub['y'], sub['pred'], zero_division=0))
        if sub['y'].nunique() > 1:
            fold_subj_auc.append(roc_auc_score(sub['y'], sub['p']))

        rec_preds.append(pd.DataFrame({
            'fold': fold, 'sid': g_te, 'y': y_te, 'p': p_te
        }))

    rec_df = pd.concat(rec_preds, ignore_index=True)
    subj_df = subject_level_metrics(rec_df['sid'].values,
                                    rec_df['y'].values,
                                    rec_df['p'].values)

    return {
        'model': model_name,
        'subj_acc_mean': np.mean(fold_subj_acc),
        'subj_acc_ci':   bootstrap_ci(np.array(fold_subj_acc)),
        'subj_f1_mean':  np.mean(fold_subj_f1),
        'subj_auc_mean': np.mean(fold_subj_auc) if fold_subj_auc else np.nan,
        'pooled_subj_auc': roc_auc_score(subj_df['y'], subj_df['p'])
                             if subj_df['y'].nunique() > 1 else np.nan,
        'rec_predictions': rec_df,
        'subj_predictions': subj_df,
    }

# ---------------------------------------------------------------------
# 6. Run Track 1 (Istanbul only) and Track 2 (+ Oxford augmentation)
# ---------------------------------------------------------------------
X_ist = ist[TIER_A].fillna(0).values
y_ist = ist['status'].astype(int).values
g_ist = ist['subject_id'].values

X_oxf = oxf[TIER_A].fillna(0).values
y_oxf = oxf['status'].astype(int).values   # all 1s
g_oxf = oxf['subject_id'].values

results = []
for name, (est, grid) in build_models().items():
    print(f"\n>>> Track 1 (Istanbul only) — {name}")
    r1 = nested_cv(X_ist, y_ist, g_ist, name, est, grid)
    r1['track'] = 'istanbul_only'
    results.append(r1)

    print(f">>> Track 2 (Istanbul + Oxford-augmented) — {name}")
    # rebuild estimator to avoid leakage of fitted state
    est2, grid2 = build_models()[name]
    r2 = nested_cv(X_ist, y_ist, g_ist, name, est2, grid2,
                   augment_X=X_oxf, augment_y=y_oxf,
                   augment_groups=g_oxf, augment_weight=0.3)
    r2['track'] = 'augmented'
    results.append(r2)

# ---------------------------------------------------------------------
# 7. Summary table
# ---------------------------------------------------------------------
summary = pd.DataFrame([{
    'track': r['track'],
    'model': r['model'],
    'subj_acc': f"{r['subj_acc_mean']:.3f} "
                f"[{r['subj_acc_ci'][0]:.3f}, {r['subj_acc_ci'][1]:.3f}]",
    'subj_f1':  f"{r['subj_f1_mean']:.3f}",
    'subj_auc_mean_folds': f"{r['subj_auc_mean']:.3f}",
    'pooled_subj_auc':     f"{r['pooled_subj_auc']:.3f}",
} for r in results])

print("\n=== Final summary (subject-level metrics) ===")
print(summary.to_string(index=False))

# ---------------------------------------------------------------------
# 8. Pick the winner and refit on all Istanbul data
# ---------------------------------------------------------------------
best_row = max(results, key=lambda r: (r['pooled_subj_auc'], r['subj_acc_mean']))
print(f"\nBest model: {best_row['model']} ({best_row['track']})  "
      f"AUC={best_row['pooled_subj_auc']:.3f}")

# Refit best model on all Istanbul (optionally + Oxford) for deployment artefact
final_est, final_grid = build_models()[best_row['model']]
gs_final = GridSearchCV(final_est, final_grid,
                        cv=list(GroupKFold(3).split(X_ist, y_ist, groups=g_ist)),
                        scoring='roc_auc', n_jobs=-1, refit=True)
gs_final.fit(X_ist, y_ist)
print(f"Best hyperparameters: {gs_final.best_params_}")

import joblib
joblib.dump({'model': gs_final.best_estimator_,
             'features': TIER_A,
             'tier': 'A',
             'training_source': 'istanbul_only'},
            'pd_status_classifier.joblib')