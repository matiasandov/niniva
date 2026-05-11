import random
import shutil
from pathlib import Path

def create_train_val_test_split(
    source_dir, 
    dest_dir, 
    pos_neg_ratio=(1, 3), 
    train_split=0.7,
    val_split=0.15,
    valid_extensions={'.wav', '.opus', '.mp3', '.flac'}
):
    """
    Creates a train/val/test dataset maintaining a specific positive-to-negative ratio.
    
    Args:
        source_dir (str/Path): Directory containing 'positive' and 'negative' subfolders.
        dest_dir (str/Path): Where the 'train', 'val', and 'test' folders will be created.
        pos_neg_ratio (tuple): The desired ratio of (positive, negative). Default is (1, 3).
        train_split (float): Percentage of data to use for training (0.0 to 1.0).
        val_split (float): Percentage of data to use for validation (0.0 to 1.0).
        valid_extensions (set): Allowed file extensions to ensure no hidden files are copied.
    """
    src_path = Path(source_dir).resolve()
    dest_path = Path(dest_dir).resolve()
    
    src_pos_dir = src_path / "positive"
    src_neg_dir = src_path / "negative"
    
    # 1. Validation Checks
    if not src_pos_dir.is_dir() or not src_neg_dir.is_dir():
        print(f"❌ Error: Could not find 'positive' and/or 'negative' folders inside {src_path}")
        return
        
    pos_files = [f for f in src_pos_dir.iterdir() if f.suffix.lower() in valid_extensions]
    neg_files = [f for f in src_neg_dir.iterdir() if f.suffix.lower() in valid_extensions]
    
    if not pos_files or not neg_files:
        print("❌ Error: One or both source directories are empty (or have no valid audio files).")
        return

    print(f"🔍 Found {len(pos_files)} positive and {len(neg_files)} negative audio files.")

    # 2. Balance / Ratio Logic
    max_neg_allowed = int(len(pos_files) * (pos_neg_ratio[1] / pos_neg_ratio[0]))
    
    if len(neg_files) > max_neg_allowed:
        random.shuffle(neg_files)
        selected_neg = neg_files[:max_neg_allowed]
        print(f"⚖️ Downsampling negative files to {max_neg_allowed} to match {pos_neg_ratio[0]}:{pos_neg_ratio[1]} ratio.")
    else:
        selected_neg = neg_files
        print("⚠️ Not enough negative files to meet the exact ratio. Using all available.")

    # 3. Shuffle
    random.shuffle(pos_files)
    random.shuffle(selected_neg)

    # 4. Calculate Split Indices
    test_split = 1.0 - (train_split + val_split)
    if test_split < 0 or test_split > 1.0:
        print("❌ Error: train_split + val_split must be less than or equal to 1.0")
        return

    pos_total = len(pos_files)
    train_pos_count = int(pos_total * train_split)
    val_pos_count = int(pos_total * val_split)

    neg_total = len(selected_neg)
    train_neg_count = int(neg_total * train_split)
    val_neg_count = int(neg_total * val_split)

    # 5. Slicing the lists into 3 segments
    train_pos_files = pos_files[:train_pos_count]
    val_pos_files = pos_files[train_pos_count : train_pos_count + val_pos_count]
    test_pos_files = pos_files[train_pos_count + val_pos_count :]

    train_neg_files = selected_neg[:train_neg_count]
    val_neg_files = selected_neg[train_neg_count : train_neg_count + val_neg_count]
    test_neg_files = selected_neg[train_neg_count + val_neg_count :]
    
    # 6. Helper function to copy files to their new home
    def copy_files(file_list, target_sub_dir):
        target_sub_dir.mkdir(parents=True, exist_ok=True)
        for f in file_list:
            shutil.copy2(f, target_sub_dir / f.name)

    print("📁 Creating directories and copying files...")
    
    # 7. Execute the copying
    copy_files(train_pos_files, dest_path / "train" / "positive")
    copy_files(train_neg_files, dest_path / "train" / "negative")
    
    copy_files(val_pos_files, dest_path / "val" / "positive")
    copy_files(val_neg_files, dest_path / "val" / "negative")

    # 👇 New test split directory creation
    copy_files(test_pos_files, dest_path / "test" / "positive")
    copy_files(test_neg_files, dest_path / "test" / "negative")
    
    print("✅ Split complete!")
    print(f"   Train set: {len(train_pos_files)} positive, {len(train_neg_files)} negative")
    print(f"   Val set:   {len(val_pos_files)} positive, {len(val_neg_files)} negative")
    print(f"   Test set:  {len(test_pos_files)} positive, {len(test_neg_files)} negative")


# ==========================================
# Example Usage
# ==========================================
# if __name__ == "__main__":
    
#     source = r"data\wakewords\stop"
#     destination = r"data\wakewords\stop\dataset_split"
    
#     # This will create a 70% Train, 15% Validation, and 15% Test split
#     create_train_val_test_split(
#         source_dir=source, 
#         dest_dir=destination, 
#         pos_neg_ratio=(1, 3), 
#         train_split=0.7,
#         val_split=0.15
#     )