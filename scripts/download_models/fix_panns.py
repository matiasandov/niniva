import os
import urllib.request

def download_panns_files():
    # 1. Define the target directory (C:\Users\matts\panns_data)
    panns_dir = os.path.expanduser('~/panns_data')
    os.makedirs(panns_dir, exist_ok=True)
    print(f"Directory ready: {panns_dir}")

    # 2. URLs for the required files
    csv_url = "https://raw.githubusercontent.com/qiuqiangkong/audioset_tagging_cnn/master/metadata/class_labels_indices.csv"
    csv_path = os.path.join(panns_dir, "class_labels_indices.csv")

    model_url = "https://zenodo.org/record/3987831/files/Cnn14_mAP%3D0.431.pth"
    model_path = os.path.join(panns_dir, "Cnn14_mAP=0.431.pth")

    # 3. Download the CSV
    if not os.path.exists(csv_path):
        print(f"Downloading {csv_path}...")
        urllib.request.urlretrieve(csv_url, csv_path)
    else:
        print("CSV already exists. Skipping.")

    # 4. Download the Model Weights (~320MB)
    if not os.path.exists(model_path):
        print(f"Downloading Cnn14 weights (This is ~320MB and might take a minute)...")
        urllib.request.urlretrieve(model_url, model_path)
    else:
        print("Model weights already exist. Skipping.")

    print("\n✅ All files successfully downloaded! You can now run your evaluation script.")