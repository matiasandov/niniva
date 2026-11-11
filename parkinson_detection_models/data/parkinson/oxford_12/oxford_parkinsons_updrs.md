Parkinsons Telemonitoring Data Set  

path: data\parkinson\oxford_12\processed_oxford_12_data.csv

Abstract: Oxford Parkinson's Disease Telemonitoring Dataset

============================================================

Data Set Characteristics:  Multivariate
Attribute Characteristics:  Integer, Real
Associated Tasks:  Regression
Number of Instances:  5875
Number of Attributes:  26
Area:  Life
Date Donated:  2009-10-29

============================================================

SOURCE:

The dataset was created by Athanasios Tsanas (tsanasthanasis '@' gmail.com) 
and Max Little (littlem '@' physics.ox.ac.uk) of the University of Oxford, in 
collaboration with 10 medical centers in the US and Intel Corporation who 
developed the telemonitoring device to record the speech signals. The 
original study used a range of linear and nonlinear regression methods to 
predict the clinician's Parkinson's disease symptom score on the UPDRS scale.


============================================================

DATA SET INFORMATION:

This dataset is composed of a range of biomedical voice measurements from 42 
people with early-stage Parkinson's disease recruited to a six-month trial of 
a telemonitoring device for remote symptom progression monitoring. The 
recordings were automatically captured in the patient's homes.

Columns in the table contain subject number, subject age, subject gender, 
time interval from baseline recruitment date, motor UPDRS, total UPDRS, and 
16 biomedical voice measures. Each row corresponds to one of 5,875 voice 
recording from these individuals. The main aim of the data is to predict the 
motor and total UPDRS scores ('motor_UPDRS' and 'total_UPDRS') from the 16 
voice measures.

The data is in ASCII CSV format. The rows of the CSV file contain an instance 
corresponding to one voice recording. There are around 200 recordings per 
patient, the subject number of the patient is identified in the first column. 
For further information or to pass on comments, please contact Athanasios 
Tsanas (tsanasthanasis '@' gmail.com) or Max Little (littlem '@' 
physics.ox.ac.uk).

Further details are contained in the following reference -- if you use this 
dataset, please cite:
Athanasios Tsanas, Max A. Little, Patrick E. McSharry, Lorraine O. Ramig (2009),
'Accurate telemonitoring of Parkinson.s disease progression by non-invasive 
speech tests',
IEEE Transactions on Biomedical Engineering (to appear).

Further details about the biomedical voice measures can be found in:
Max A. Little, Patrick E. McSharry, Eric J. Hunter, Lorraine O. Ramig (2009),
'Suitability of dysphonia measurements for telemonitoring of Parkinson's 
disease',
IEEE Transactions on Biomedical Engineering, 56(4):1015-1022 

 
===========================================================

ATTRIBUTE INFORMATION:

subject_id - Integer that uniquely identifies each subject
age - Subject age
sex - Subject gender '0' - male, '1' - female
test_time - Time since recruitment into the trial. The integer part is the 
number of days since recruitment.
motor_UPDRS - Clinician's motor UPDRS score, linearly interpolated
total_UPDRS - Clinician's total UPDRS score, linearly interpolated
Jitter(%),Jitter(Abs),Jitter:RAP,Jitter:PPQ5,Jitter:DDP - Several measures of 
variation in fundamental frequency
Shimmer,Shimmer(dB),Shimmer:APQ3,Shimmer:APQ5,Shimmer:APQ11,Shimmer:DDA - 
Several measures of variation in amplitude
NHR,HNR - Two measures of ratio of noise to tonal components in the voice
RPDE - A nonlinear dynamical complexity measure
DFA - Signal fractal scaling exponent
PPE - A nonlinear measure of fundamental frequency variation 


===========================================================

RELEVANT PAPERS:

Little MA, McSharry PE, Hunter EJ, Ramig LO (2009),
'Suitability of dysphonia measurements for telemonitoring of Parkinson's 
disease',
IEEE Transactions on Biomedical Engineering, 56(4):1015-1022

Little MA, McSharry PE, Roberts SJ, Costello DAE, Moroz IM.
'Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice 
Disorder Detection',
BioMedical Engineering OnLine 2007, 6:23 (26 June 2007) 

===========================================================

CITATION REQUEST:

If you use this dataset, please cite the following paper:
A Tsanas, MA Little, PE McSharry, LO Ramig (2009)
'Accurate telemonitoring of Parkinson.s disease progression by non-invasive 
speech tests',
IEEE Transactions on Biomedical Engineering (to appear). 

# Row sample (scaled acoustic features)

subject_id,age,sex,test_time,motor_UPDRS,total_UPDRS,Jitter(%),Jitter(Abs),Jitter:RAP,Jitter:PPQ5,Jitter:DDP,Shimmer,Shimmer(dB),Shimmer:APQ3,Shimmer:APQ5,Shimmer:APQ11,Shimmer:DDA,NHR,HNR,RPDE,DFA,PPE,UPDRS_change,UPDRS_Severity,day,motor_UPDRS_change,status,source
1,72,0,5.6431,28.199,34.398,0.00662,3.38e-05,0.00401,0.00317,0.01204,0.02565,0.23,0.01438,0.01309,0.01662,0.04314,0.01429,21.64,0.41888,0.54842,0.16006,0.0,Moderate (20-35),6.0,0.0,1,oxford_12_parkinsons_updrs_data


Scaled features with StandardScaler:

acoustic_features = [
    'Jitter(%)', 'Jitter(Abs)', 'Jitter:RAP', 'Jitter:PPQ5', 'Jitter:DDP',
    'Shimmer', 'Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5', 'Shimmer:APQ11', 
    'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA', 'PPE'
]