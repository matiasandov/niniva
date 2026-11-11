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

def print_directory_tree(directory_path, prefix="", exclude_extensions=None):
    """Prints the directory tree, hiding files with specific extensions."""
    
    # Initialize the exclude list safely
    if exclude_extensions is None:
        exclude_extensions = set()
    else:
        # Normalize the extensions: make them lowercase and ensure they start with a dot
        # This means passing "txt" or ".TXT" will both work perfectly
        exclude_extensions = {
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
            for ext in exclude_extensions
        }

    path = Path(directory_path)
    
    # Base case for the root directory
    if prefix == "":
        if not path.is_dir():
            print("Error: Directory does not exist.")
            return
        print(f"📁 {path.name}/")
        
    # Gather items, filtering out the files we want to exclude
    items = []
    for item in path.iterdir():
        if item.is_dir():
            items.append(item)
        # Only add the file if its extension (.suffix) is NOT in our exclusion list
        elif item.is_file() and item.suffix.lower() not in exclude_extensions:
            items.append(item)
            
    # Sort them (folders first, then files, both alphabetically)
    items.sort(key=lambda x: (x.is_file(), x.name.lower()))
    
    total_items = len(items)
    
    for index, item in enumerate(items):
        is_last = (index == total_items - 1)
        connector = "└── " if is_last else "├── "
        
        if item.is_dir():
            print(f"{prefix}{connector}📁 {item.name}/")
            extension = "    " if is_last else "│   "
            
            # CRITICAL: Pass the exclude_extensions down to the sub-folders!
            print_directory_tree(
                item, 
                prefix=prefix + extension, 
                exclude_extensions=exclude_extensions
            )
        else:
            print(f"{prefix}{connector}📄 {item.name}")

# --- Example Usage ---
# Exclude Python cache files and markdown files
print_directory_tree('data', exclude_extensions=['.opus', '.md','.wav' ,'.venv'])

# Example usage:
#breakdown_files_per_nested_folder('data\wakewords\stop')
# Example usage:
#print(count_files_recursively('data\wakewords\stop\positive'))  # Replace with your directory path
#print(count_files_recursively('data\wakewords\stop'))
