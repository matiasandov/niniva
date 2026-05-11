# Setup your parameters
from scripts.data.create_train_val_data_from_pos_and_neg import create_train_val_test_split
from scripts.data.opus_to_wav import convert_opus_to_wav_pydub
from scripts.data.selecting_negative_samples import sample_audio_files

# 1. Pick random negative samples for wake word (stop)
# ADDED 'r' prefix here
all_samples = r"data\all_wake_words"
    
# Exclude the positive files 
# ADDED 'r' prefix AND wrapped in [] to make it a list
folders_to_skip = [r"data\all_wake_words\mswc_microset\en\clips\stop"]

# ADDED 'r' prefix here (This is the one that caused the crash!)
negative_destination_folder = r"data\wakewords\stop\negative"

amount_to_pick = 8500

sample_audio_files(
    input_dir=all_samples,
    num_files=amount_to_pick,
    exclude_dirs=folders_to_skip,
    dest_dir=negative_destination_folder
)

print(f"✅ Sampled {amount_to_pick} negative files to {negative_destination_folder}")

#Create Train/Val splits with the desired positive:negative ratio

source = r"data\wakewords\stop"         # Must contain /positive and /negative
destination = r"data\wakewords\stop\dataset_split"     # Will create /train and /val inside here
    
create_train_val_test_split(
        source_dir=source, 
        dest_dir=destination, 
        pos_neg_ratio=(1, 3), 
        train_split=0.7,
        val_split=0.15
    )

print(f"✅ Created train/val splits in {destination}")

# 3. Convert any .opus files to .wav (if needed)
convert_opus_to_wav_pydub(destination)