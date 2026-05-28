"""
Parkinson's Disease Classification — Istanbul Dataset (full 24-feature set)
===========================================================================
Best practices baked in (per Cincović et al., 2026 review + prior lessons):
  - Subject-independent nested CV (GroupKFold outer + inner) -> no leakage
  - Multi-model comparison (paper Table 7: SVM, RF, XGBoost, LightGBM, KNN, NB, LogReg)
  - Recording -> subject-level aggregation (mean probability)
  - Bootstrap 95% CIs on metrics (paper Section 4.2 stresses variability reporting)
  - Independent test set used as external PD-sensitivity check
  - Probability-first output (predict_proba), thresholded only at reporting
  - Full reproducible artifacts saved (model + config + metrics)
"""

import os, json, datetime, glob
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                             recall_score, precision_score, confusion_matrix)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 0. Config
# ============================================================
RNG = 42
BASE_DIR = "c:/Users/matts/Desktop/wakeup-ai"
DATA_PATH = "data/parkinson/istanbul_updrs/processed_istanbul_updrs_data_scaled.csv"
SAVE_ROOT = "saved_models/istanbul_updrs_only_model"

os.chdir(BASE_DIR)

FEATURES = [
    'jitter_local', 'jitter_local_abs', 'jitter_rap', 'jitter_ppq5', 'jitter_ddp',
    'shimmer_local', 'shimmer_local_db', 'shimmer_apq3', 'shimmer_apq5',
    'shimmer_apq11', 'shimmer_dda', 'ac', 'nth', 'htn',
    'pitch_median', 'pitch_mean', 'pitch_std', 'pitch_min', 'pitch_max',
    'num_pulses', 'mean_period', 'std_period',
    'unvoiced_frames_frac', 'degree_voice_breaks'
]  # 24 scaled features (num_periods & num_voice_breaks dropped as redundant)

TARGET = 'class_label'
GROUP  = 'subject_id'

# ============================================================
# 1. Load and split train / independent test
# ============================================================
df = pd.read_csv(DATA_PATH)

train_df = df[df['source'] == 'istanbul_train'].copy()
test_df  = df[df['source'] == 'istanbul_test'].copy()   # all PD, external check

X = train_df[FEATURES].values
y = train_df[TARGET].astype(int).values
g = train_df[GROUP].astype(str).values

print(f"Train: {len(train_df)} recordings, {train_df[GROUP].nunique()} subjects, "
      f"class balance {pd.Series(y).value_counts().to_dict()}")
if len(test_df):
    print(f"Independent test: {len(test_df)} recordings, "
          f"{test_df[GROUP].nunique()} subjects "
          f"(all PD: {test_df[TARGET].nunique()==1 and test_df[TARGET].iloc[0]==1})")

# ============================================================
# 2. Model zoo (paper-recommended for engineered voice features)
# ============================================================
def build_models():
    return {
        'LogReg': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', LogisticRegression(max_iter=2000,
                                                 class_weight='balanced'))]),
            {'clf__C': [0.1, 1.0, 10.0]}
        ),
        'NaiveBayes': (
            Pipeline([('sc', StandardScaler()), ('clf', GaussianNB())]),
            {'clf__var_smoothing': [1e-9, 1e-7]}
        ),
        'KNN': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', KNeighborsClassifier())]),
            {'clf__n_neighbors': [5, 9, 15], 'clf__weights': ['uniform', 'distance']}
        ),
        'SVM-RBF': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', SVC(kernel='rbf', probability=True,
                                  class_weight='balanced', random_state=RNG))]),
            {'clf__C': [0.5, 1, 5, 10], 'clf__gamma': ['scale', 0.1, 0.01]}
        ),
        'RandomForest': (
            RandomForestClassifier(class_weight='balanced',
                                   random_state=RNG, n_jobs=-1),
            {'n_estimators': [300, 600], 'max_depth': [None, 8, 12],
             'min_samples_leaf': [1, 3]}
        ),
        'XGBoost': (
            XGBClassifier(eval_metric='logloss', random_state=RNG,
                          n_jobs=-1, verbosity=0),
            {'n_estimators': [300, 500], 'max_depth': [4, 6],
             'learning_rate': [0.05, 0.1], 'subsample': [0.8, 1.0]}
        ),
        'LightGBM': (
            LGBMClassifier(class_weight='balanced', random_state=RNG,
                           n_jobs=-1, verbosity=-1),
            {'n_estimators': [300, 500], 'num_leaves': [15, 31],
             'learning_rate': [0.05, 0.1]}
        ),
    }

# ============================================================
# 3. Helpers: subject aggregation, bootstrap CI
# ============================================================
def subject_level(subject_ids, y_true, y_prob, threshold=0.5):
    out = (pd.DataFrame({'sid': subject_ids, 'y': y_true, 'p': y_prob})
             .groupby('sid')
             .agg(y=('y', 'first'), p=('p', 'mean'))
             .reset_index())
    out['pred'] = (out['p'] >= threshold).astype(int)
    return out

def bootstrap_ci(values, n_boot=2000, alpha=0.05):
    rng = np.random.default_rng(RNG)
    values = np.asarray(values)
    boots = [np.mean(rng.choice(values, len(values), replace=True))
             for _ in range(n_boot)]
    return float(np.percentile(boots, 100*alpha/2)), \
           float(np.percentile(boots, 100*(1-alpha/2)))

# ============================================================
# 4. Nested CV
# ============================================================
def nested_cv(X, y, groups, name, estimator, grid,
              n_outer=5, n_inner=3):
    outer = GroupKFold(n_splits=n_outer)
    inner = GroupKFold(n_splits=n_inner)

    fold_acc, fold_f1, fold_auc, fold_sens, fold_spec = [], [], [], [], []
    rec_rows = []
    best_params_per_fold = []

    for fold, (tr, te) in enumerate(outer.split(X, y, groups=groups)):
        gs = GridSearchCV(
            estimator, grid,
            cv=list(inner.split(X[tr], y[tr], groups=groups[tr])),
            scoring='roc_auc', n_jobs=-1, refit=True
        )
        gs.fit(X[tr], y[tr])
        best = gs.best_estimator_
        best_params_per_fold.append(gs.best_params_)

        p_te = best.predict_proba(X[te])[:, 1]
        sub = subject_level(groups[te], y[te], p_te)

        fold_acc.append(accuracy_score(sub['y'], sub['pred']))
        fold_f1.append(f1_score(sub['y'], sub['pred'], zero_division=0))
        fold_sens.append(recall_score(sub['y'], sub['pred'],
                                      pos_label=1, zero_division=0))
        fold_spec.append(recall_score(sub['y'], sub['pred'],
                                      pos_label=0, zero_division=0))
        if sub['y'].nunique() > 1:
            fold_auc.append(roc_auc_score(sub['y'], sub['p']))

        rec_rows.append(pd.DataFrame({'fold': fold, 'sid': groups[te],
                                      'y': y[te], 'p': p_te}))

    rec_df = pd.concat(rec_rows, ignore_index=True)
    pooled = subject_level(rec_df['sid'].values, rec_df['y'].values,
                           rec_df['p'].values)

    return {
        'model': name,
        'acc_mean': float(np.mean(fold_acc)),
        'acc_ci': bootstrap_ci(fold_acc),
        'f1_mean': float(np.mean(fold_f1)),
        'sens_mean': float(np.mean(fold_sens)),
        'spec_mean': float(np.mean(fold_spec)),
        'auc_mean_folds': float(np.mean(fold_auc)) if fold_auc else np.nan,
        'pooled_auc': float(roc_auc_score(pooled['y'], pooled['p']))
                      if pooled['y'].nunique() > 1 else np.nan,
        'best_params_per_fold': best_params_per_fold,
        'subj_predictions': pooled,
    }

# ============================================================
# 5. Run all models
# ============================================================
results = []
for name, (est, grid) in build_models().items():
    print(f">>> Nested CV — {name}")
    results.append(nested_cv(X, y, g, name, est, grid))

summary = pd.DataFrame([{
    'model': r['model'],
    'acc': f"{r['acc_mean']:.3f} [{r['acc_ci'][0]:.3f}, {r['acc_ci'][1]:.3f}]",
    'f1': f"{r['f1_mean']:.3f}",
    'sensitivity': f"{r['sens_mean']:.3f}",
    'specificity': f"{r['spec_mean']:.3f}",
    'auc_folds': f"{r['auc_mean_folds']:.3f}",
    'pooled_auc': f"{r['pooled_auc']:.3f}",
} for r in results])

print("\n=== Subject-level summary ===")
print(summary.to_string(index=False))

# ============================================================
# 6. Pick best model (AUC primary, F1 tiebreak) and refit on ALL train
# ============================================================
best = max(results, key=lambda r: (r['pooled_auc'], r['f1_mean']))
print(f"\nBest model: {best['model']}  "
      f"(pooled AUC={best['pooled_auc']:.3f}, F1={best['f1_mean']:.3f})")

final_est, final_grid = build_models()[best['model']]
gs_final = GridSearchCV(
    final_est, final_grid,
    cv=list(GroupKFold(5).split(X, y, groups=g)),
    scoring='roc_auc', n_jobs=-1, refit=True
)
gs_final.fit(X, y)
final_model = gs_final.best_estimator_
print(f"Final hyperparameters: {gs_final.best_params_}")

# ============================================================
# 7. Feature importance (permutation, model-agnostic)
# ============================================================
perm = permutation_importance(final_model, X, y, n_repeats=30,
                              random_state=RNG, scoring='roc_auc', n_jobs=-1)
fi = (pd.DataFrame({'feature': FEATURES,
                    'importance': perm.importances_mean,
                    'std': perm.importances_std})
        .sort_values('importance', ascending=False)
        .reset_index(drop=True))
print("\n=== Permutation feature importance (AUC drop) ===")
print(fi.head(10).to_string(index=False))

# ============================================================
# 8. Calibration (subject-level, from best model's CV predictions)
# ============================================================
sp = best['subj_predictions']
brier = float(np.mean((sp['p'] - sp['y'])**2))
frac_pos, mean_pred = calibration_curve(sp['y'], sp['p'],
                                        n_bins=5, strategy='quantile')
print(f"\n=== Calibration (subject-level) ===  Brier={brier:.3f}")
for mp, fp in zip(mean_pred, frac_pos):
    print(f"  predicted ~{mp:.2f}  ->  actual PD rate {fp:.2f}")

# ============================================================
# 9. Independent test set: PD sensitivity (external validation)
# ============================================================
ext = None
if len(test_df):
    Xt = test_df[FEATURES].values
    pt = final_model.predict_proba(Xt)[:, 1]
    sub_t = subject_level(test_df[GROUP].astype(str).values,
                          test_df[TARGET].astype(int).values, pt)
    ext_sens = float(recall_score(sub_t['y'], sub_t['pred'],
                                  pos_label=1, zero_division=0))
    ext = {'n_subjects': int(sub_t.shape[0]),
           'pd_sensitivity_subject_level': ext_sens,
           'mean_pd_probability': float(sub_t['p'].mean())}
    print(f"\n=== Independent test (all-PD) ===")
    print(f"Subjects: {ext['n_subjects']}  "
          f"PD sensitivity: {ext_sens:.3f}  "
          f"mean P(PD): {ext['mean_pd_probability']:.3f}")

# ============================================================
# 10. Save everything (model + config + metrics + extras)
# ============================================================
def save_run(best, all_results, final_model, final_params,
             summary_df, fi_df, calib, ext, base=SAVE_ROOT):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(base, f"run_{ts}_{best['model']}")
    os.makedirs(run_dir, exist_ok=True)

    joblib.dump({'model': final_model,
                 'features': FEATURES,
                 'target': TARGET,
                 'dataset': 'istanbul_train (full 24 features)',
                 'output': 'predict_proba[:,1] = P(class_label=1, i.e. PD)',
                 'decision_threshold': 0.5,
                 'aggregation': 'mean probability across a subject recordings'},
                os.path.join(run_dir, "model.joblib"))

    config = {
        'timestamp': ts,
        'best_model': best['model'],
        'final_hyperparameters': final_params,
        'best_params_per_outer_fold': best['best_params_per_fold'],
        'features': FEATURES, 'n_features': len(FEATURES),
        'target': TARGET, 'group_key': GROUP,
        'cv': {'outer': 'GroupKFold(5)', 'inner': 'GroupKFold(3)',
               'scoring': 'roc_auc'},
        'decision_threshold': 0.5,
        'random_seed': RNG,
        'data_path': DATA_PATH,
    }
    with open(os.path.join(run_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    metrics = [{
        'model': r['model'],
        'acc_mean': r['acc_mean'], 'acc_ci_low': r['acc_ci'][0],
        'acc_ci_high': r['acc_ci'][1], 'f1_mean': r['f1_mean'],
        'sensitivity': r['sens_mean'], 'specificity': r['spec_mean'],
        'auc_mean_folds': r['auc_mean_folds'], 'pooled_auc': r['pooled_auc'],
    } for r in all_results]
    with open(os.path.join(run_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    summary_df.to_csv(os.path.join(run_dir, "results_summary.csv"), index=False)
    fi_df.to_csv(os.path.join(run_dir, "feature_importance.csv"), index=False)
    best['subj_predictions'].to_csv(
        os.path.join(run_dir, "subject_predictions_cv.csv"), index=False)

    with open(os.path.join(run_dir, "calibration.json"), "w") as f:
        json.dump(calib, f, indent=2)
    if ext is not None:
        with open(os.path.join(run_dir, "external_test.json"), "w") as f:
            json.dump(ext, f, indent=2)

    print(f"\n✅ Run saved to: {run_dir}")
    return run_dir

calib_payload = {'brier': brier,
                 'mean_predicted': mean_pred.tolist(),
                 'fraction_positive': frac_pos.tolist()}

run_dir = save_run(best, results, final_model, gs_final.best_params_,
                   summary, fi, calib_payload, ext)

# ============================================================
# 11. Cross-run benchmark helper
# ============================================================
def benchmark_runs(base=SAVE_ROOT):
    rows = []
    for mp in glob.glob(os.path.join(base, "run_*", "metrics.json")):
        run = os.path.basename(os.path.dirname(mp))
        for m in json.load(open(mp)):
            m['run'] = run
            rows.append(m)
    return pd.DataFrame(rows)

# bench = benchmark_runs(); print(bench.sort_values('pooled_auc', ascending=False))
