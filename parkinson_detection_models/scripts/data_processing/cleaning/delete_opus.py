from pathlib import Path

def delete_opus_files(directory_path):
    """
    Finds and deletes all .opus files in the given directory and its subdirectories.
    
    Args:
        directory_path (str/Path): The target directory to clean up.
    """
    path = Path(directory_path).resolve()
    
    if not path.is_dir():
        print(f"❌ Error: The directory '{path}' does not exist.")
        return

    # Find all .opus files recursively
    opus_files = list(path.rglob('*.opus'))
    
    if not opus_files:
        print(f"ℹ️ No .opus files found in '{path.name}'.")
        return
        
    print(f"Found {len(opus_files)} .opus files. Starting deletion...\n" + "-"*40)
    
    deleted_count = 0
    failed_count = 0
    
    for file_path in opus_files:
        try:
            # .unlink() is the pathlib command to delete a file
            file_path.unlink()
            deleted_count += 1
            # Optional: print(f"Deleted: {file_path.name}")
        except Exception as e:
            print(f"⚠️ Failed to delete {file_path.name}: {e}")
            failed_count += 1

    print("\n✅ Cleanup Complete!")
    print(f"🗑️ Successfully deleted: {deleted_count}")
    if failed_count > 0:
        print(f"❌ Failed to delete: {failed_count}")

# ==========================================
# Example Usage
# ==========================================
# if __name__ == "__main__":
    
#     # Be very careful with the path you provide here!
#     target_directory = "data\wakewords\stop\positive"
    
#     delete_opus_files(target_directory)