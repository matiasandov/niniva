import os
import time
import json
import psutil
import torch
import numpy as np
from torch.utils.data import DataLoader, Subset
from panns_inference import AudioTagging, labels as panns_labels

# Your custom imports
from src.dataset_urban_sound import UrbanSoundDataset

def evaluate_base_cnn14_baseline(data_root, metadata_csv, limit_samples=None, output_dir="results/baseline"):
    print(f"🔍 Evaluating Pre-trained Base CNN14 (Zero-Shot Baseline)")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Initialize PANNs
    at = AudioTagging(checkpoint_path=None, device=device)
    
    # Calculate Disk Size of the downloaded model
    checkpoint_path = os.path.join(os.path.expanduser('~'), 'panns_data', 'Cnn14_mAP=0.431.pth')
    disk_size_mb = os.path.getsize(checkpoint_path) / (1024 * 1024) if os.path.exists(checkpoint_path) else 0

    # 2. Load Dataset
    test_ds = UrbanSoundDataset(
        root=data_root,
        metadata_csv=metadata_csv,
        folds=[10], 
        sample_rate=32000, 
        clip_seconds=4.0,  
        augment=False,
    )
    dataset_class_names = test_ds.class_names

    if limit_samples is not None:
        actual_limit = min(limit_samples, len(test_ds))
        test_ds = Subset(test_ds, range(actual_limit))
        print(f"⚠️ QUICK TEST MODE: {actual_limit} samples.")

    test_loader = DataLoader(test_ds, batch_size=16, shuffle=False, num_workers=0) # Set workers to 0 for cleaner RAM tracking

    # 3. Run Inference & Benchmarking
    print("\n🏃 Running predictions...")
    all_probs, true_labels = [], []
    
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    start_time = time.perf_counter()
    
    for wav, label in test_loader:
        wav_np = wav.numpy() 
        if wav_np.ndim == 3:
            wav_np = wav_np.squeeze(1) 
            
        clipwise_output, _ = at.inference(wav_np)
        
        all_probs.append(clipwise_output)
        true_labels.append(label.numpy())

    end_time = time.perf_counter()
    
    # 4. Calculate Final Benchmarks
    total_samples = len(test_ds)
    total_time = end_time - start_time
    avg_time_ms = (total_time / total_samples) * 1000
    
    process = psutil.Process(os.getpid())
    peak_ram_mb = process.memory_info().rss / (1024 * 1024)
    peak_vram_mb = torch.cuda.max_memory_allocated(device) / (1024 * 1024) if device == "cuda" else 0.0

    all_probs = np.concatenate(all_probs)
    true_labels = np.concatenate(true_labels)

    # 5. Output Results to Console
    print("\n" + "=" * 50)
    print("🚀 BASELINE BENCHMARK METRICS")
    print("=" * 50)
    print(f"Weights Disk Size: {disk_size_mb:.2f} MB")
    print(f"Avg Time / Sample: {avg_time_ms:.2f} ms")
    print(f"Peak System RAM  : {peak_ram_mb:.2f} MB")
    if device == "cuda":
        print(f"Peak GPU VRAM    : {peak_vram_mb:.2f} MB")

    # 6. Save results to JSON
    results = {
        "model_type": "cnn14_base_audioset",
        "benchmarks": {
            "disk_size_mb": float(f"{disk_size_mb:.2f}"),
            "avg_inference_time_ms": float(f"{avg_time_ms:.2f}"),
            "peak_system_ram_mb": float(f"{peak_ram_mb:.2f}"),
            "peak_gpu_vram_mb": float(f"{peak_vram_mb:.2f}")
        },
        "samples_evaluated": total_samples
    }
    
    res_path = os.path.join(output_dir, "baseline_eval.json")
    with open(res_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n💾 Results saved to: {res_path}")

if __name__ == "__main__":
    DATA_ROOT = r"data\audio_data\sounds"
    METADATA_CSV = os.path.join(DATA_ROOT, "UrbanSound8K.csv")
    
    # Run the base CNN14 with benchmarks and saving enabled
    evaluate_base_cnn14_baseline(DATA_ROOT, METADATA_CSV, limit_samples=100)