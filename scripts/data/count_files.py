from pathlib import Path

#absolute count
def count_files_recursively(directory_path):
    """Counts all files in the directory and all its subdirectories."""
    path = Path(directory_path)
    
    if not path.is_dir():
        return "Error: Directory does not exist."
        
    # rglob('*') recursively goes through everything in the directory tree
    file_count = sum(1 for item in path.rglob('*') if item.is_file())
    
    return file_count

from pathlib import Path

def breakdown_files_per_nested_folder(directory_path):
    """Prints every single subdirectory and the number of files directly inside it."""
    root_path = Path(directory_path)
    
    if not root_path.is_dir():
        print("Error: Directory does not exist.")
        return

    print(f"Detailed breakdown for: {root_path.name}\n" + "-"*30)

    # Create a list containing the root directory PLUS all its nested subdirectories
    all_folders = [root_path] + [d for d in root_path.rglob('*') if d.is_dir()]

    for folder in all_folders:
        # Count only the files immediately inside this specific folder
        file_count = sum(1 for item in folder.iterdir() if item.is_file())
        
        # Optional: Skip printing folders that are completely empty
        if file_count > 0:
            # Get the relative path so the output isn't excessively long
            try:
                display_name = folder.relative_to(root_path)
                if str(display_name) == '.':
                    display_name = "(Root Directory)"
            except ValueError:
                display_name = folder.name
                
            print(f"[{display_name}] -> {file_count} files")

# Example usage:
breakdown_files_per_nested_folder('data\wakewords\stop')
# Example usage:
#print(count_files_recursively('data\wakewords\stop\positive'))  # Replace with your directory path
#print(count_files_recursively('data\wakewords\stop'))
