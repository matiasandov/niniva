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
status. Data and analyses include Istanbul and Oxford datasets, as well as
combined voice-data experiments. Training and evaluation scripts compare
classical machine-learning approaches such as logistic regression, SVM,
random forest, XGBoost, LightGBM, K-nearest neighbors, and Naive Bayes.
Subject-grouped cross-validation is used in the Istanbul-only evaluation to
reduce leakage between recordings from the same subject.

Saved artifacts and evaluation outputs are under
[`parkinson_detection_models/saved_models/`](./parkinson_detection_models/saved_models/)
and [`parkinson_detection_models/results/`](./parkinson_detection_models/results/).
For example, the Istanbul-only experiment includes a saved XGBoost model,
configuration, and evaluation results.

### CRNN audio experiments

The repository also includes Tiny-CRNN models, including smaller parameter
variants, built from convolutional and recurrent layers with an optional
attention layer. These experiments cover audio classification and wakeword or
sound-event tasks; they are separate from the Parkinson's voice-feature
classifiers and should not be interpreted as Parkinson's diagnostic models.

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
