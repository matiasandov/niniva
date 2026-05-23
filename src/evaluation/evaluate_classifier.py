import os
import time
import json
import psutil
import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    f1_score,
    top_k_accuracy_score,
)

from src.dataset_urban_sound import UrbanSoundDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN

# Import PANNs models
try:
    from panns_inference.models import Cnn14
except ImportError:
    Cnn14 = None


class EndToEndModel(torch.nn.Module):
    def __init__(self, feature_extractor, crnn_model):
        super().__init__()
        self.fe = feature_extractor
        self.model = crnn_model

    def forward(self, x):
        feats = self.fe(x)
        return self.model(feats)


def load_model_from_config(config, run_dir, device):
    model_type = config.get("model_type", "tiny_crnn")
    weights_path = os.path.join(run_dir, "model.pth")
    
    if model_type == "tiny_crnn":
        feature_extractor = LFBEFeatureExtractor(
            sample_rate=config["sample_rate"],
            n_mels=config["n_mels"],
            n_frames=config["n_frames"],
        )
        model = TinyCRNN(
            n_mels=config["n_mels"],
            n_frames=config["n_frames"],
            conv_channels=config["conv_channels"],
            gru_hidden=config["gru_hidden"],
            fc_hidden=config["fc_hidden"],
            use_attention=config["use_attention"],
            num_classes=config["num_classes"],
        )
        model.load_state_dict(torch.load(weights_path, map_location=device))
        return EndToEndModel(feature_extractor, model).to(device).eval(), model_type
        
    elif model_type == "cnn14":
        if Cnn14 is None:
            raise ImportError("Please install panns_inference to evaluate CNN14.")
        
        model = Cnn14(
            sample_rate=config["sample_rate"], 
            window_size=1024, 
            hop_size=320, 
            mel_bins=64, 
            fmin=50, 
            fmax=14000, 
            classes_num=config["num_classes"]
        )
        model.load_state_dict(torch.load(weights_path, map_location=device))
        return model.to(device).eval(), model_type
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")


@torch.no_grad()
def collect_predictions(model, loader, device, model_type):
    all_probs, all_labels = [], []
    
    # Reset CUDA memory stats before tracking inference memory footprint
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        
    print("\n🏃 Running predictions (tracking time and compute)...")
    
    # High precision timer start
    start_time = time.perf_counter()
    
    for wav, label in loader:
        wav = wav.to(device)
        
        if model_type == "cnn14":
            if wav.dim() == 3:
                wav = wav.squeeze(1) 
            outputs = model(wav)
            probs = outputs['clipwise_output'] 
        elif model_type == "tiny_crnn":
            logits = model(wav)
            probs = torch.softmax(logits, dim=1)
            
        all_probs.append(probs.cpu().numpy())
        all_labels.append(label.numpy())
        
    # High precision timer end
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    return np.concatenate(all_probs), np.concatenate(all_labels), total_time


def plot_confusion_matrix(cm, class_names, save_path, normalize=True):
    if normalize:
        cm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1e-9)

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=1 if normalize else None)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(len(class_names)),
        yticks=np.arange(len(class_names)),
        xticklabels=class_names,
        yticklabels=class_names,
        ylabel="True label",
        xlabel="Predicted label",
        title="Confusion Matrix" + (" (normalized)" if normalize else ""),
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontsize=8)

    fig.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)


def evaluate_model(run_dir, data_root, metadata_csv):
    print(f"🔍 Evaluating model from: {run_dir}")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    with open(os.path.join(run_dir, "config.json"), "r") as f:
        config = json.load(f)

    # 1. Build Model & Get Parameter Count
    model, model_type = load_model_from_config(config, run_dir, device)
    
    weights_path = os.path.join(run_dir, "model.pth")
    disk_size_mb = os.path.getsize(weights_path) / (1024 * 1024)
    total_params = sum(p.numel() for p in model.parameters())
    
    print(f"✅ Model Loaded. Architecture: {model_type.upper()} ({disk_size_mb:.2f} MB, {total_params:,} parameters)")

    # 2. Setup Data
    test_ds = UrbanSoundDataset(
        root=data_root,
        metadata_csv=metadata_csv,
        folds=config["test_folds"],
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=False,
    )
    test_loader = DataLoader(test_ds, batch_size=config["batch_size"],
                             shuffle=False, num_workers=2)

    class_names = config.get("class_names") or test_ds.class_names

    # 3. Predict & Measure Time/Memory
    probs, labels, total_inference_time = collect_predictions(model, test_loader, device, model_type)
    preds = probs.argmax(axis=1)

    # Calculate Benchmark Metrics
    total_samples = len(test_ds)
    avg_time_ms = (total_inference_time / total_samples) * 1000  # Convert to milliseconds
    
    # Get peak memory usage (System RAM + GPU VRAM if available)
    process = psutil.Process(os.getpid())
    peak_ram_mb = process.memory_info().rss / (1024 * 1024)
    peak_vram_mb = torch.cuda.max_memory_allocated(device) / (1024 * 1024) if device == "cuda" else 0.0

    # 4. Model Accuracy Metrics
    acc = accuracy_score(labels, preds)
    macro_f1 = f1_score(labels, preds, average="macro")
    weighted_f1 = f1_score(labels, preds, average="weighted")
    top3 = top_k_accuracy_score(labels, probs, k=3,
                                labels=np.arange(config["num_classes"]))

    cm = confusion_matrix(labels, preds, labels=np.arange(config["num_classes"]))
    report_dict = classification_report(
        labels, preds,
        labels=np.arange(config["num_classes"]),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    # 5. Print Output
    print("\n" + "=" * 50)
    print("🚀 BENCHMARK METRICS")
    print("=" * 50)
    print(f"Model Parameters : {total_params:,}")
    print(f"Weights Disk Size: {disk_size_mb:.2f} MB")
    print(f"Avg Time / Sample: {avg_time_ms:.2f} ms")
    print(f"Peak System RAM  : {peak_ram_mb:.2f} MB")
    if device == "cuda":
        print(f"Peak GPU VRAM    : {peak_vram_mb:.2f} MB")
        
    print("\n" + "=" * 50)
    print("📊 CLASSIFICATION RESULTS")
    print("=" * 50)
    print(f"Accuracy         : {acc:.4f}")
    print(f"Top-3 Accuracy   : {top3:.4f}")
    print(f"Macro F1         : {macro_f1:.4f}")
    print(f"Weighted F1      : {weighted_f1:.4f}")

    # 6. Save results with benchmarks
    results = {
        "metadata": {
            "model_type": model_type,
            "test_samples": total_samples,
            "device": device
        },
        "benchmarks": {
            "parameters_count": total_params,
            "disk_size_mb": float(f"{disk_size_mb:.2f}"),
            "avg_inference_time_ms": float(f"{avg_time_ms:.2f}"),
            "peak_system_ram_mb": float(f"{peak_ram_mb:.2f}"),
            "peak_gpu_vram_mb": float(f"{peak_vram_mb:.2f}")
        },
        "metrics": {
            "accuracy": float(acc),
            "top3_accuracy": float(top3),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "per_class": report_dict,
            "confusion_matrix": cm.tolist(),
            "class_names": class_names,
        }
    }
    
    with open(os.path.join(run_dir, "eval_results.json"), "w") as f:
        json.dump(results, f, indent=4)

    # 7. Plots
    plot_confusion_matrix(cm, class_names,
                          os.path.join(run_dir, "confusion_matrix.png"),
                          normalize=True)
    plot_confusion_matrix(cm, class_names,
                          os.path.join(run_dir, "confusion_matrix_counts.png"),
                          normalize=False)


if __name__ == "__main__":
    RUN_TO_EVALUATE = r"saved_models\sound_events\tiny_crnn_urbansound_v20260510_222414"
    DATA_ROOT = r"data\audio_data\sounds"
    METADATA_CSV = os.path.join(DATA_ROOT, "UrbanSound8K.csv")

    evaluate_model(RUN_TO_EVALUATE, DATA_ROOT, METADATA_CSV)