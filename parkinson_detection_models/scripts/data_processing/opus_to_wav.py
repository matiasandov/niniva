from pathlib import Path
from pydub import AudioSegment

def convert_opus_to_wav_pydub(directory_path):
    """Converts all .opus files to .wav using the pydub library, then deletes the original."""
    path = Path(directory_path)
    
    if not path.is_dir():
        print("Error: Directory does not exist.")
        return

    opus_files = list(path.rglob('*.opus'))
    
    if not opus_files:
        print(f"No .opus files found in {path.name}")
        return

    print(f"Found {len(opus_files)} .opus files. Starting conversion...\n" + "-"*30)

    for opus_file in opus_files:
        wav_file = opus_file.with_suffix('.wav')
        print(f"Converting: {opus_file.name} -> {wav_file.name}")
        
        try:
            # Load the opus file and export it as wav
            audio = AudioSegment.from_file(opus_file)
            audio.export(wav_file, format="wav")
            
            # --- NEW LINE ADDED HERE ---
            # Delete the original .opus file only if the export was successful
            opus_file.unlink()
            
        except Exception as e:
            print(f"❌ Failed to convert {opus_file.name}: {e}")

    print("\n✅ Conversion and cleanup complete!")

# Example usage:
#convert_opus_to_wav_pydub('data\wakewords\stop')