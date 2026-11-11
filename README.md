<p align="center">
  <img src="./assets/niniva-logo.svg" alt="Niniva logo" width="88" height="88">
</p>

# Niniva

Niniva brings together a clinician-facing neurologist assistant app and a
research workspace for Parkinson's-related machine-learning experiments. The
app and research code live in separate directories:

- [`frontend/`](./frontend/) contains the web application.
- [`parkinson_detection_models/`](./parkinson_detection_models/) contains
  Python data, experiments, training scripts, evaluation results, and saved
  model artifacts.

## App goal

The web app is intended to help neurologists organize and review patient
information. Its current interface includes a clinical dashboard, patient
list and profiles, and patient-focused clinical information. The goal is to
support a clinician's workflow and make relevant information easier to review;
it is not a replacement for clinical judgment.

The frontend is a standalone app. The repository currently keeps it separate
from the model experiments; it should not be assumed that the saved research
models are connected to the app for inference.

## Model and research work

The model workspace contains several exploratory tracks:

### Parkinson's voice-feature classification

The Parkinson's experiments use tabular voice measurements, including voice
quality and pitch-related features, to explore classification of Parkinson's
status and symptom severity. The workspace contains several source datasets
and variants:

- **Istanbul Parkinson's speech datasets** include recordings from people with
  Parkinson's and healthy controls, with acoustic voice features and, in some
  variants, clinical scores. The data folder includes both the Istanbul speech
  features dataset and an Istanbul UPDRS dataset.
- **Oxford Parkinson's telemonitoring dataset** contains thousands of repeated
  voice recordings from 42 people with Parkinson's, acoustic measurements,
  and motor and total UPDRS scores recorded over time. It does not provide
  healthy controls.
- **Combined Istanbul + Oxford voice data** harmonizes overlapping acoustic
  features and adds source, subject, diagnosis, and clinical-score fields.
  Some columns are source-specific or imputed, and differences in recording
  protocols and feature extraction mean that combining the datasets can
  introduce domain shift.
- **Other Parkinson's data** in the workspace includes an Alemán speech/EGG
  sample and additional Oxford data files and analyses. These are stored
  research resources; they are not all inputs to the combined classifier.

The combined-data work is best understood as **multi-source, multi-feature
research**, not as a single neural network that fuses raw audio and patient
records. The PD-versus-healthy experiment compares Istanbul-only training
with an Istanbul experiment augmented by Oxford PD recordings. Its shared
Tier A inputs are 13 numerical measurements derived from each voice
recording:

- **Jitter (pitch-period variation):** `Jitter(%)`, `Jitter(Abs)`,
  `Jitter:RAP`, `Jitter:PPQ5`, and `Jitter:DDP`.
- **Shimmer (voice-amplitude variation):** `Shimmer`, `Shimmer(dB)`,
  `Shimmer:APQ3`, `Shimmer:APQ5`, `Shimmer:APQ11`, and `Shimmer:DDA`.
- **Voice noise/tonality:** `NHR` (noise-to-harmonics ratio) and `HNR`
  (harmonics-to-noise ratio).

Each row represents a recording's extracted acoustic features, not raw audio.
The target is the binary diagnosis/status label. Oxford contributes
Parkinson's recordings only, as additional positive-class training data; it
does not add healthy controls. UPDRS scores, severity fields, demographics,
and other acoustic columns in the combined dataset are not inputs to this
particular 13-feature comparison. The dataset includes other measurements
and clinical fields for separate analyses, some with provenance flags for
imputed values.

The training scripts compare classical machine-learning approaches such as
logistic regression, SVM, random forest, XGBoost, LightGBM, K-nearest
neighbors, and Naive Bayes. Subject-grouped cross-validation keeps recordings
from the same person together when evaluating a model, reducing the risk that
the evaluation benefits from seeing that person's other recordings during
training.

### Reported experiment results

The strongest reported Parkinson's classification result is from the
Istanbul + Oxford-augmented comparison: **XGBoost** had a pooled subject-level
AUC of **0.740**, with mean subject-level accuracy of **0.675** and F1 of
**0.708**. The best Istanbul-only result by pooled subject-level AUC in that
comparison was **SVM-RBF** at **0.720**. These are cross-validation results,
not independent external validation. The experiment also measured a
source-detection AUC of **1.000**, indicating substantial differences between
the Istanbul and Oxford data; the augmented result should therefore be
interpreted cautiously. Although XGBoost won the augmented-track comparison,
the script's final saved classifier is refit on Istanbul-only data.

A separate saved Istanbul-only evaluation reports a different ranking:
**XGBoost** had the highest pooled AUC (**0.710**), while **KNN** had the
highest F1 (**0.709**). Logistic regression and LightGBM had the highest mean
accuracy (**0.675**, tied). These results are from a different evaluation
artifact and should not be combined with the augmented comparison as if they
were one leaderboard.

For the non-Parkinson's audio tasks, the saved Tiny-CRNN wakeword evaluation
reports **97.4% accuracy** and **0.993 ROC-AUC** on 1,441 test samples. The
saved UrbanSound8K sound-event evaluation reports **70.0% accuracy** and
**90.2% top-3 accuracy** on 837 samples. These audio-classification results
measure different tasks and datasets, so they are not comparable to the
Parkinson's classification metrics.

Saved artifacts and evaluation outputs are under
[`parkinson_detection_models/saved_models/`](./parkinson_detection_models/saved_models/)
and [`parkinson_detection_models/results/`](./parkinson_detection_models/results/).
For example, the Istanbul-only experiment includes a saved XGBoost model,
configuration, and evaluation results.

### CRNN audio experiments

**Tiny-CRNN** means a compact convolutional recurrent neural network for
classifying short audio clips. Audio is represented as a time-by-frequency
feature map (log filter-bank energies, or LFBE). Convolutional layers learn
local patterns in that map, a gated recurrent unit (GRU) learns how those
patterns change over time, and an optional attention layer lets the network
weight informative time steps before its classification head produces a
prediction. The small model size is intended for efficient audio
classification; the default architecture is documented as roughly 239,000
parameters, with smaller variants also provided.

The CRNN experiments cover wakeword and general sound-event classification.
The workspace includes UrbanSound8K data for sound-event work as well as
wakeword data and scripts. These are separate audio tasks: the Tiny-CRNN
models are not the Parkinson's voice-feature classifiers and should not be
interpreted as Parkinson's diagnostic models.

## Running the frontend

From the `frontend/` directory, install dependencies and start the Vite
development server:

```sh
pnpm install
pnpm dev
```

## Python research workspace

The model workspace uses Poetry and declares Python 3.11 through 3.13 support
in [`parkinson_detection_models/pyproject.toml`](./parkinson_detection_models/pyproject.toml).
For environment setup, consult that project's configuration and the
experiment-specific scripts and documentation. Dataset paths and commands may
depend on which experiment is being run.

## Research and clinical-use notice

The models and reported results are research artifacts, not validated medical
devices. They are not intended to diagnose, treat, or rule out Parkinson's
disease. Do not use their predictions as a substitute for assessment by a
qualified healthcare professional.
