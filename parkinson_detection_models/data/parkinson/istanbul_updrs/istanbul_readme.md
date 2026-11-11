# istanbul_updrs
Here's a full breakdown of all 29 columns, mapped to your sample row:

path to dataset: data\parkinson\istanbul_updrs\processed_istanbul_updrs_data_scaled.csv

## instances

The PD database consists of training and test files. The training data belongs to 20 PWP (6 female, 14 male) and 20 healthy individuals (10 female, 10 male) who appealed at the Department of Neurology in Cerrahpasa Faculty of Medicine, Istanbul University. From all subjects, multiple types of sound recordings (26 voice samples including sustained vowels, numbers, words and short sentences) are taken.  A group of 26 linear and timeâ€“frequency based features are extracted from each voice sample. UPDRS ((Unified Parkinsonâ€™s Disease Rating Scale) score of each patient which is determined by expert physician is also available in this dataset. Therefore, this dataset can also be used for regression.

After collecting the training dataset which consists of multiple types of sound recordings and performing our experiments, in line with the obtained findings we continued collecting an independent test set from PWP via the same physicianâ€™s examination process under the same conditions. During the collection of this dataset, 28 PD patients are asked to say only the sustained vowels 'a' and 'o' three times respectively which makes a total of 168 recordings. The same 26 features are extracted from voice samples of this dataset. This dataset can be used as an independent test set to validate the results obtained on training set.

Further details are contained in the following reference -- if you use this dataset, please cite: 
Erdogdu Sakar, B., Isenkul, M., Sakar, C.O., Sertbas, A., Gurgen, F., Delil, S., Apaydin, H., Kursun,
O., 'Collection and Analysis of a Parkinson Speech Dataset with Multiple Types of Sound
Recordings', IEEE Journal of Biomedical and Health Informatics, vol. 17(4), pp. 828-834, 2013

Training Data File:
Each subject has 26 voice samples including sustained vowels, numbers, words and short 
sentences. The voice samples in the training data file are given in the 
following order:

sample# - corresponding voice samples
1: sustained vowel (aaaâ€¦â€¦)
2: sustained vowel (oooâ€¦...)
3: sustained vowel (uuuâ€¦...)
4-13: numbers from 1 to 10
14-17: short sentences
18-26: words

Test Data File:
28 PD patients are asked to say only the sustained vowels 'a' and 'o' three times respectively which makes a total of 168 recordings (each subject has 6 voice samples) The voice samples in the test data file are given in the following order:

sample# - corresponding voice samples
1-3: sustained vowel (aaaâ€¦â€¦)
4-6: sustained vowel (oooâ€¦â€¦)

---

**Sample row:**

subject_id,jitter_local,jitter_local_abs,jitter_rap,jitter_ppq5,jitter_ddp,shimmer_local,shimmer_local_db,shimmer_apq3,shimmer_apq5,shimmer_apq11,shimmer_dda,ac,nth,htn,pitch_median,pitch_mean,pitch_std,pitch_min,pitch_max,num_pulses,num_periods,mean_period,std_period,unvoiced_frames_frac,num_voice_breaks,degree_voice_breaks,updrs,class_label,source
1,-0.6753883691856436,-0.7535966744564015,-0.35450054072780157,-0.48702324960526744,-0.3548351376729896,-0.8412370941447667,-0.9905361863733312,-0.3924038436159505,-0.697428386451291,-0.9002185885664656,-0.3924085240772452,0.6991147704275712,-0.7424268771885145,0.26355676133729783,0.05651806827498145,-0.07054717726921983,-0.46723870111878635,0.16351289643221759,-0.3893554614196023,0.33513775747636154,159,-0.2570851185906801,-0.5897889686114098,-1.320418878047633,0,-0.8162552610291124,23,1,istanbul_train

---

### Col 1 — Subject ID
`1` — The identifier for the subject (patient or healthy person).

---

### Cols 2–6 — Jitter (vocal frequency variation)
Jitter measures how much the pitch/frequency varies from cycle to cycle. Higher jitter = less stable voice, common in Parkinson's.

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 2 | Jitter (local) | 0.728 | Cycle-to-cycle variation as a % of period |
| 3 | Jitter (local, absolute) | 0.0000377 | Same but in seconds (absolute time) |
| 4 | Jitter (RAP) | 0.353 | Relative Average Perturbation — avg over 3 cycles |
| 5 | Jitter (PPQ5) | 0.376 | 5-point Period Perturbation Quotient |
| 6 | Jitter (DDP) | 1.059 | Average absolute diff between consecutive differences (= RAP × 3) |

---

### Cols 7–12 — Shimmer (vocal amplitude variation)
Shimmer measures how much the loudness/amplitude varies. Higher shimmer = irregular amplitude, also a Parkinson's indicator.

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 7 | Shimmer (local) | 5.864 | Cycle-to-cycle amplitude variation (%) |
| 8 | Shimmer (local, dB) | 0.642 | Same but in decibels |
| 9 | Shimmer (APQ3) | 2.058 | 3-point Amplitude Perturbation Quotient |
| 10 | Shimmer (APQ5) | 3.18 | 5-point Amplitude Perturbation Quotient |
| 11 | Shimmer (APQ11) | 7.194 | 11-point Amplitude Perturbation Quotient |
| 12 | Shimmer (DDA) | 6.175 | Avg absolute diff between consecutive amplitude differences (= APQ3 × 3) |

---

### Cols 13–15 — Harmonics / Noise Ratios
These measure the ratio of harmonic (tonal) signal to noise in the voice.

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 13 | AC (Autocorrelation) | 0.951285 | Degree of periodicity in the signal (0–1, higher = more regular) |
| 14 | NTH (Noise-to-Harmonics) | 0.066758 | Noise relative to harmonics — higher = noisier voice |
| 15 | HTN (Harmonics-to-Noise) | 17.403 | Inverse of NTH — higher = cleaner, more harmonic voice |

---

### Cols 16–20 — Pitch Statistics (in Hz)

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 16 | Median pitch | 195.252 Hz | Middle pitch value across the recording |
| 17 | Mean pitch | 193.289 Hz | Average pitch |
| 18 | Std deviation of pitch | 14.773 Hz | How much pitch fluctuates |
| 19 | Minimum pitch | 159.515 Hz | Lowest pitch detected |
| 20 | Maximum pitch | 234.505 Hz | Highest pitch detected |

---

### Cols 21–24 — Pulse / Period Statistics

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 21 | Number of pulses | 170 | Total glottal pulses counted in the recording |
| 22 | Number of periods | 169 | Total vocal periods (one less than pulses) |
| 23 | Mean period | 0.005181 s | Average duration of one vocal cycle (~5.2 ms) |
| 24 | Std deviation of period | 0.000403 s | Variability in period duration |

---

### Cols 25–27 — Voicing / Voice Break Features

| Col | Feature | Value | Meaning |
|-----|---------|-------|---------|
| 25 | Fraction of locally unvoiced frames | 2.247 | % of frames where voice drops out |
| 26 | Number of voice breaks | 0 | Count of complete voice interruptions |
| 27 | Degree of voice breaks | 0 | Total duration of breaks as % of signal |

---

### Col 28 — UPDRS Score
`23` — The **Unified Parkinson's Disease Rating Scale** score, assigned by a physician. Only present for PD patients (0 for healthy subjects). Higher = more severe symptoms. Used for **regression** tasks.

### Col 29 — Class Label
`1` — The target for **classification**: `1` = Parkinson's patient, `0` = healthy subject.

---

**In summary**, the features capture three main dimensions of voice quality: pitch stability (jitter), amplitude stability (shimmer), and noise/harmonic structure — all of which degrade measurably with Parkinson's disease.

Scaled features with StandardScaler:

acoustic_features = [
    'jitter_local', 'jitter_local_abs', 'jitter_rap',
       'jitter_ppq5', 'jitter_ddp', 'shimmer_local', 'shimmer_local_db',
       'shimmer_apq3', 'shimmer_apq5', 'shimmer_apq11', 'shimmer_dda', 'ac',
       'nth', 'htn', 'pitch_median', 'pitch_mean', 'pitch_std', 'pitch_min',
       'pitch_max', 'num_pulses', 'mean_period', 'std_period',
       'unvoiced_frames_frac', "degree_voice_breaks"
]