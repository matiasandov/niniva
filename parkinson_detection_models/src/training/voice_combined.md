Istanbul: 1040 recordings, 40 subjects, class balance: {1: 520, 0: 520}
Oxford  : 5875 recordings, 42 subjects (all PD)

[Diagnostic] Source-detection AUC = 1.000 (>0.7 indicates strong domain shift)

>>> Track 1 (Istanbul only) — LogReg
>>> Track 2 (Istanbul + Oxford-augmented) — LogReg

>>> Track 1 (Istanbul only) — SVM-RBF
>>> Track 2 (Istanbul + Oxford-augmented) — SVM-RBF

>>> Track 1 (Istanbul only) — RandomForest
>>> Track 2 (Istanbul + Oxford-augmented) — RandomForest

>>> Track 1 (Istanbul only) — XGBoost
>>> Track 2 (Istanbul + Oxford-augmented) — XGBoost

>>> Track 1 (Istanbul only) — LightGBM
>>> Track 2 (Istanbul + Oxford-augmented) — LightGBM

=== Final summary (subject-level metrics) ===
        track        model             subj_acc subj_f1 subj_auc_mean_folds pooled_subj_auc
istanbul_only       LogReg 0.575 [0.450, 0.700]   0.567               0.690           0.682
    augmented       LogReg 0.500 [0.425, 0.575]   0.000               0.641           0.620
istanbul_only      SVM-RBF 0.675 [0.575, 0.750]   0.683               0.742           0.720
    augmented      SVM-RBF 0.550 [0.450, 0.650]   0.498               0.631           0.608
istanbul_only RandomForest 0.675 [0.575, 0.800]   0.685               0.663           0.685
    augmented RandomForest 0.550 [0.450, 0.625]   0.160               0.739           0.665
istanbul_only      XGBoost 0.650 [0.550, 0.750]   0.680               0.704           0.688
    augmented      XGBoost 0.675 [0.550, 0.800]   0.708               0.741           0.740
istanbul_only     LightGBM 0.675 [0.575, 0.800]   0.708               0.691           0.695
    augmented     LightGBM 0.550 [0.450, 0.675]   0.248               0.728           0.672

Best model: XGBoost (augmented)  AUC=0.740
Best hyperparameters: {'learning_rate': 0.05, 'max_depth': 4, 'n_estimators': 300, 'subsample': 0.8}