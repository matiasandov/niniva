import random
import shutil
from pathlib import Path

def sample_audio_files(input_dir, num_files, exclude_dirs, dest_dir):
    """
    Randomly selects audio files from a directory and copies them to a new location.
    
    Args:
        input_dir (str/Path): The main folder containing the audio files.
        num_files (int): How many files to randomly pick.
        exclude_dirs (list): A list of directory paths to ignore.
        dest_dir (str/Path): Where the picked files should be copied to.
    """
    # 1. Normalize all paths to be absolute (resolves issues with relative paths like '.' or '..')
    input_path = Path(input_dir).resolve()
    dest_path = Path(dest_dir).resolve()
    
    # Convert exclude list to a set of resolved Path objects for accurate comparison
    exclude_paths = {Path(d).resolve() for d in exclude_dirs}
    
    # Ensure the destination directory exists (creates it if it doesn't)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Standard audio extensions
    audio_exts = {'.wav', '.mp3', '.opus', '.flac', '.ogg', '.m4a'}
    valid_files = []
    
    # 2. Gather all valid files
    for file_path in input_path.rglob('*'):
        if not file_path.is_file():
            continue
            
        # Skip if it's not an audio file
        if file_path.suffix.lower() not in audio_exts:
            continue
            
        # Check if this file lives inside ANY of the excluded directories
        # .parents returns a sequence of all the folders this file is nested inside
        resolved_file = file_path.resolve()
        if any(ex_dir in resolved_file.parents for ex_dir in exclude_paths):
            continue
            
        valid_files.append(resolved_file)
        
    # 3. Handle edge cases where there aren't enough files
    if not valid_files:
        print("Error: No valid audio files found outside of the excluded directories.")
        return
        
    if len(valid_files) < num_files:
        print(f"⚠️ Warning: You asked for {num_files} files, but only found {len(valid_files)}.")
        print("Selecting all available files instead.")
        num_files = len(valid_files)
        
    # 4. Randomly sample the exact number of files requested
    selected_files = random.sample(valid_files, num_files)
    
    print(f"Found {len(valid_files)} eligible files. Copying {num_files} to '{dest_path.name}'...\n" + "-"*40)
    
    # 5. Copy the files to the destination
    for i, file_path in enumerate(selected_files):
        dest_file = dest_path / file_path.name
        
        # Collision Check: If a file with this name already exists in the destination, 
        # append the current loop index to the filename to make it unique.
        if dest_file.exists():
            new_name = f"{file_path.stem}_copy{i}{file_path.suffix}"
            dest_file = dest_path / new_name
            
        # Copy the file along with its metadata (creation dates, etc.)
        shutil.copy2(file_path, dest_file)
        
    print(f"✅ Successfully copied {num_files} files to: {dest_path}")

# ==========================================
# Example Usage based on your project structure
# ==========================================
# if __name__ == "__main__":
    
#     # Setup your parameters
#     main_audio_folder = r"data\wakewords\stop"
    
#     # Exclude the 'negative' folder
#     folders_to_skip = [
#         r"data\wakewords\stop\negative"
#     ]
    
#     destination_folder = r"data\wakewords\sampled_dataset"
    
#     amount_to_pick = 50
    
#     # Run the function
#     sample_audio_files(
#         input_dir=main_audio_folder,
#         num_files=amount_to_pick,
#         exclude_dirs=folders_to_skip,
#         dest_dir=destination_folder
#     )