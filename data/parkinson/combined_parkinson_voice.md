# Combined Parkinson's Disease Voice Dataset — README & Working Skill

> **Purpose of this document:** Serve as both a reference README for the combined dataset and a reusable "skill" / playbook for future work. Anyone (or any agent) picking up this dataset should be able to read this file and immediately know what the data is, where it came from, how it was assembled, what to trust, and how to model it correctly.

---

## 1. Overview

This dataset is a **harmonized combination of two publicly available Parkinson's Disease (PD) voice datasets**:

1. **Oxford Parkinson's Telemonitoring Dataset** (Tsanas, Little et al., 2009) — the **master** dataset.
2. **Istanbul Parkinson's Speech Dataset** (Erdogdu Sakar et al., 2013) — secondary dataset providing healthy controls and additional acoustic dimensions.

The combined file contains per-recording acoustic voice features, UPDRS scores, severity bins, and provenance flags indicating which values are original vs. imputed.

- **File:** `combined_parkinson_voice.csv`
- **Rows:** ~7,000+ voice recordings (5,875 Oxford + ~1,200 Istanbul)
- **Granularity:** one row = one voice recording
- **Subjects:** 42 PD (Oxford) + 20 PD + 20 healthy (Istanbul train) + 28 PD (Istanbul test)

---

## 2. Data Origins

### 2.1 Oxford Telemonitoring Dataset (master)
- 42 early-stage PD patients, ~200 recordings each over a 6-month at-home telemonitoring trial.
- Recorded automatically in patients' homes via an Intel telemonitoring device.
- Includes **interpolated motor and total UPDRS** (continuous, longitudinal).
- Provides **nonlinear features** (RPDE, DFA, PPE) not present in Istanbul.
- All subjects are PD — **no healthy controls**.

### 2.2 Istanbul Speech Dataset (secondary)
- 40 training subjects (20 PD + 20 healthy) recorded in clinic at the Department of Neurology, Cerrahpasa Faculty of Medicine, Istanbul University.
- 28 additional PD patients in the independent test set.
- Recordings include sustained vowels, numbers, words, short sentences (training); only vowels 'a' and 'o' (test).
- Features extracted with Praat — overlap conceptually with Oxford but were extracted with a **different pipeline**.
- Provides **healthy controls** and **pitch/pulse/voice-break features** not present in Oxford.
- UPDRS is a **single physician-assigned score per subject** (not interpolated).

### ⚠️ Critical caveat
Even features with the same name (e.g., `Jitter:RAP`) come from different extraction tools and recording protocols. Absolute values are **not directly comparable** across sources. Both datasets were StandardScaled independently before merging, and the combined acoustic block is re-scaled jointly during assembly — but **domain shift remains**.

---

## 3. Column Dictionary

### 3.1 Identifiers & Metadata
| Column | Type | Description |
|---|---|---|
| `subject_id` | string | Prefixed unique ID: `OXF_<n>` or `IST_<n>`. |
| `source` | categorical | `oxford` or `istanbul_train` / `istanbul_test`. |
| `status` | int (0/1) | 1 = Parkinson's patient, 0 = healthy. All Oxford rows are 1. |

### 3.2 Clinical Targets
| Column | Type | Description |
|---|---|---|
| `total_UPDRS` | float | Unified Parkinson's Disease Rating Scale total score. Oxford: linearly interpolated by clinicians. Istanbul: single physician score. Healthy controls = 0. |
| `motor_UPDRS` | float | Motor sub-score of UPDRS. **Original in Oxford**; **imputed in Istanbul** via linear regression from `total_UPDRS` trained on Oxford. |
| `UPDRS_Severity` | categorical | Severity bin derived from `total_UPDRS`: `Mild (<20)`, `Moderate (20-35)`, `Severe (>35)`. Applied uniformly to both sources. |
| `motor_UPDRS_imputed` | int (0/1) | 1 if `motor_UPDRS` was imputed (all Istanbul rows). |

### 3.3 Overlapping Acoustic Features (present in both sources — high confidence)

**Jitter** — cycle-to-cycle pitch variation; elevated in PD.
| Column | Description |
|---|---|
| `Jitter(%)` | Local jitter as % of period. |
| `Jitter(Abs)` | Local jitter in absolute seconds. |
| `Jitter:RAP` | Relative Average Perturbation (3-cycle window). |
| `Jitter:PPQ5` | 5-point Period Perturbation Quotient. |
| `Jitter:DDP` | Avg abs diff between consecutive period differences (= RAP × 3). |

**Shimmer** — cycle-to-cycle amplitude variation; elevated in PD.
| Column | Description |
|---|---|
| `Shimmer` | Local shimmer (%). |
| `Shimmer(dB)` | Local shimmer in dB. |
| `Shimmer:APQ3` | 3-point Amplitude Perturbation Quotient. |
| `Shimmer:APQ5` | 5-point Amplitude Perturbation Quotient. |
| `Shimmer:APQ11` | 11-point Amplitude Perturbation Quotient. |
| `Shimmer:DDA` | Avg abs diff between consecutive amplitude differences (= APQ3 × 3). |

**Noise / Harmonics**
| Column | Description |
|---|---|
| `NHR` | Noise-to-Harmonics Ratio (Istanbul `nth` mapped here). Higher = noisier voice. |
| `HNR` | Harmonics-to-Noise Ratio (Istanbul `htn` mapped here). Higher = cleaner voice. |

### 3.4 Oxford-only Features (imputed for Istanbul via Random Forest regression)
Nonlinear dynamical measures, strongly correlated with UPDRS severity.

| Column | Description |
|---|---|
| `RPDE` | Recurrence Period Density Entropy — nonlinear complexity. |
| `DFA` | Detrended Fluctuation Analysis — signal fractal scaling exponent. |
| `PPE` | Pitch Period Entropy — nonlinear fundamental-frequency variation measure. |
| `RPDE_imputed` / `DFA_imputed` / `PPE_imputed` | 1 if the value was imputed (all Istanbul rows). |

> Imputation model: `RandomForestRegressor(n_estimators=300)` trained on Oxford using the 13 overlapping acoustic features as inputs. Training R² is printed at build time — **inspect it before trusting these for Istanbul subjects individually**.

### 3.5 Istanbul-only Features (NaN for Oxford rows)
Pitch, pulse, and voicing statistics extracted by Praat.

| Column | Description |
|---|---|
| `ac` | Autocorrelation (0–1); periodicity strength. |
| `pitch_median` | Median pitch (Hz, scaled). |
| `pitch_mean` | Mean pitch. |
| `pitch_std` | Std deviation of pitch. |
| `pitch_min` | Minimum pitch. |
| `pitch_max` | Maximum pitch. |
| `num_pulses` | Total glottal pulses in recording. |
| `mean_period` | Mean vocal period (s). |
| `std_period` | Std deviation of period. |
| `unvoiced_frames_frac` | Fraction of unvoiced frames. |
| `degree_voice_breaks` | Total break duration as % of signal. |

---

## 4. How the Dataset Was Built (Provenance)

1. **Renaming:** Istanbul columns renamed to Oxford convention (`jitter_rap` → `Jitter:RAP`, etc.).
2. **Severity derivation:** Istanbul gained `UPDRS_Severity` via the same bins used in Oxford (`<20`, `20–35`, `>35`).
3. **Imputation of Oxford-only nonlinear features (RPDE, DFA, PPE) for Istanbul:**
   - Trained a Random Forest regressor on Oxford (overlapping features → target).
   - Predictions written into Istanbul rows; `*_imputed` flags set to 1.
4. **Imputation of `motor_UPDRS` for Istanbul:**
   - Trained a Linear Regression on Oxford (`total_UPDRS` → `motor_UPDRS`).
   - Predictions written into Istanbul rows; flag set.
5. **Unique IDs:** Subjects prefixed `OXF_` / `IST_` to prevent collisions.
6. **Concatenation + joint re-scaling:** Acoustic block re-fit with StandardScaler across the combined data so distributions live in a shared space.
7. **Provenance preserved:** `source` and all `_imputed` flags retained for downstream filtering and weighting.

---

## 5. Modeling Tiers

The combined dataset supports two modeling regimes. **Always pick a tier explicitly before training.**

### Tier A — High Confidence (recommended default)
- **Features:** the 13 overlapping acoustic features only.
- **Targets:** `status`, `UPDRS_Severity`, optionally `total_UPDRS`.
- **Rows:** the full combined dataset.
- **Use when:** building robust classifiers/regressors that generalize across recording conditions, or when reporting results publicly.

### Tier B — Full Feature
- **Features:** all acoustic features (overlap + Oxford-only + Istanbul-only).
- **Caveat:** Istanbul rows have imputed RPDE/DFA/PPE; Oxford rows have NaN for pitch/pulse/voice-break features.
- **Recommended approach:**
  - Either restrict training to Oxford and use Istanbul for external validation,
  - Or include `source` as a covariate to absorb domain shift,
  - Or apply domain adaptation (ComBat / CORAL) before fitting.
- **Use when:** doing exploratory analysis, representation learning, or transfer-learning experiments.

---

## 6. Recommendations & Best Practices

1. **Always keep `source` and `_imputed` flags** in any analysis pipeline. They allow downstream filtering, weighting, or stratified evaluation.
2. **Do not over-trust imputed RPDE / DFA / PPE for Istanbul individuals.** Use them for aggregate analysis or as weak features. Always inspect the training R² emitted by the build script.
3. **Beware domain shift.** A quick diagnostic: train a logistic regression to predict `source` from the 13 overlapping features. If AUC ≫ 0.5, the two domains differ — apply ComBat or CORAL if serious modeling.
4. **Healthy controls (status=0) all map to `Mild (<20)` severity** because UPDRS=0. Consider creating a separate `Healthy` category instead of using severity bins for them.
5. **Repeated measures matter.** Oxford has ~200 recordings per subject. Always use **subject-level grouping in cross-validation** (`GroupKFold` on `subject_id`) to avoid leakage.
6. **Class imbalance:** Oxford (5,875) dominates Istanbul (~1,200) at the recording level. Consider per-subject aggregation or sample weighting depending on the task.
7. **When precise clinical UPDRS regression is the goal,** prefer to keep the datasets separate and use one for training, the other for validation. The combined set is best for severity classification, exploratory work, and pretraining.
8. **Re-scaling note:** the combined acoustic block was StandardScaled after concatenation. If you subset rows (e.g., only Istanbul), re-fit the scaler on the subset.

---

## 7. Reusable Skill — Quick Workflow

When returning to this dataset:

```text
1. Load combined_parkinson_voice.csv
2. Decide your task:
     - Classification (PD vs healthy)  -> use `status`, Tier A features
     - Severity classification          -> use `UPDRS_Severity`, Tier A
     - UPDRS regression                 -> Oxford only, or Tier B w/ source covariate
3. Set up GroupKFold on subject_id
4. Filter out imputed values if your analysis requires ground truth only:
       df = df[df['RPDE_imputed'] == 0]   # keeps Oxford only
5. Report metrics separately per `source` to expose domain shift
6. If using Tier B, run the source-prediction AUC diagnostic first
```

### Standard imports & loading snippet
```python
import pandas as pd
from sklearn.model_selection import GroupKFold

df = pd.read_csv("combined_parkinson_voice.csv")

OVERLAP = ['Jitter(%)','Jitter(Abs)','Jitter:RAP','Jitter:PPQ5','Jitter:DDP',
           'Shimmer','Shimmer(dB)','Shimmer:APQ3','Shimmer:APQ5','Shimmer:APQ11',
           'Shimmer:DDA','NHR','HNR']
OXFORD_ONLY   = ['RPDE','DFA','PPE']
ISTANBUL_ONLY = ['ac','pitch_median','pitch_mean','pitch_std','pitch_min',
                 'pitch_max','num_pulses','mean_period','std_period',
                 'unvoiced_frames_frac','degree_voice_breaks']

TIER_A = OVERLAP
TIER_B = OVERLAP + OXFORD_ONLY + ISTANBUL_ONLY

gkf = GroupKFold(n_splits=5)
splits = gkf.split(df, df['UPDRS_Severity'], groups=df['subject_id'])
```

---

## 8. Citations

If you use this combined dataset, cite **both** original sources:

- Tsanas A, Little MA, McSharry PE, Ramig LO (2009). *Accurate telemonitoring of Parkinson's disease progression by non-invasive speech tests.* IEEE Transactions on Biomedical Engineering.
- Erdogdu Sakar B, Isenkul M, Sakar CO, Sertbas A, Gurgen F, Delil S, Apaydin H, Kursun O (2013). *Collection and Analysis of a Parkinson Speech Dataset with Multiple Types of Sound Recordings.* IEEE Journal of Biomedical and Health Informatics, 17(4), 828–834.

---

## 9. Known Limitations

- Different recording environments (home vs clinic) and extraction tools introduce **non-trivial domain shift** even after joint scaling.
- Imputed columns (`RPDE`, `DFA`, `PPE`, `motor_UPDRS` for Istanbul) are **estimates**, not measurements.
- Istanbul UPDRS is per-subject; replicating it across all of a subject's recordings creates artificial within-subject homogeneity.
- Severity bins are coarse; consider treating UPDRS as continuous when possible.

---

*Last updated: maintained alongside the build script that produces `combined_parkinson_voice.csv`. If the build script changes (e.g., new imputation model), update Sections 4 and 6 accordingly.*
