from sklearn.model_selection import cross_val_score, GroupKFold

# (a) Honest CV-R^2 on Oxford
gkf = GroupKFold(n_splits=5)
for target in ['RPDE', 'DFA', 'PPE']:
    scores = cross_val_score(
        RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        oxf[OVERLAP], oxf[target],
        groups=oxf['subject_id'], cv=gkf, scoring='r2'
    )
    print(f"{target} CV R^2 = {scores.mean():.3f} ± {scores.std():.3f}")

# (b) Are imputed Istanbul values inside Oxford's range?
for t in ['RPDE', 'DFA', 'PPE']:
    o_lo, o_hi = oxf[t].quantile([0.01, 0.99])
    inside = ist[t].between(o_lo, o_hi).mean()
    print(f"{t}: {inside:.1%} of imputed Istanbul values inside Oxford's 1-99% range")
