import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, accuracy_score

from src.dataset import WakewordAudioDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN
from src.eval import collect_scores, fa_at_miss_rate, det_curve

class EndToEndModel(torch.nn.Module):
    """
    A simple wrapper to chain the feature extractor and the CRNN.
    This allows eval.py's collect_scores to pass raw audio (x) directly to the model.
    """
    def __init__(self, feature_extractor, crnn_model):
        super().__init__()
        self.fe = feature_extractor
        self.model = crnn_model

    def forward(self, x):
        feats = self.fe(x)
        return self.model(feats)

def evaluate_model(run_dir, test_data_path):
    print(f"🔍 Evaluating model from: {run_dir}")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. Load the Configuration
    config_path = os.path.join(run_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Could not find config.json in {run_dir}")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    print("✅ Configuration loaded.")

    # 2. Rebuild the Feature Extractor and Model exactly as they were trained
    feature_extractor = LFBEFeatureExtractor(
        sample_rate=config["sample_rate"], 
        n_mels=config["n_mels"], 
        n_frames=config["n_frames"]
    )
    
    model = TinyCRNN(
        n_mels=config["n_mels"], 
        n_frames=config["n_frames"],
        conv_channels=config["conv_channels"]
    )

    # 3. Load the Saved Weights
    model_path = os.path.join(run_dir, "model.pth")
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("✅ Model weights loaded.")

    # 4. Wrap for Evaluation
    e2e_model = EndToEndModel(feature_extractor, model).to(device)
    e2e_model.eval()

    # 5. Prepare Test Dataset (Note: augment=False)
    test_ds = WakewordAudioDataset(
        root=test_data_path,
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=False  # 👈 No augmentation during evaluation!
    )
    test_loader = DataLoader(test_ds, batch_size=config["batch_size"], shuffle=False, num_workers=2)
    print(f"📂 Test dataset loaded: {len(test_ds)} samples")

    # ==========================================
    # RUN EVALUATION METRICS
    # ==========================================
    print("\n🏃‍♂️ Running predictions on test set...")
    scores, labels = collect_scores(e2e_model, test_loader, device)

    # Calculate Standard Metrics
    predictions = (scores >= 0.5).astype(int)
    acc = accuracy_score(labels, predictions)
    auc = roc_auc_score(labels, scores)

    # Calculate Custom Eval Metrics from eval.py
    target_miss_rate = 0.15
    fa, optimal_threshold = fa_at_miss_rate(scores, labels, target_miss_rate=target_miss_rate)
    
    fdr, miss = det_curve(scores, labels)

    print("\n" + "="*40)
    print("📊 EVALUATION RESULTS")
    print("="*40)
    print(f"Accuracy:                  {acc:.4f}")
    print(f"ROC-AUC:                   {auc:.4f}")
    print(f"Optimal Threshold (15% MR): {optimal_threshold:.4f}")
    print(f"False Accepts at 15% MR:    {fa}")
    print("="*40)

    # Save results to a JSON file in the run directory
    results = {
        "test_samples": len(test_ds),
        "accuracy": acc,
        "roc_auc": auc,
        "target_miss_rate": target_miss_rate,
        "optimal_threshold": float(optimal_threshold),
        "false_accepts": int(fa)
    }
    
    with open(os.path.join(run_dir, "eval_results.json"), "w") as f:
        json.dump(results, f, indent=4)

    # Plot and save DET Curve
    plt.figure(figsize=(8, 6))
    plt.plot(fdr, miss, color='blue', lw=2, label='DET Curve')
    plt.plot(fdr[np.argmin(np.abs(miss - target_miss_rate))], target_miss_rate, 'ro', 
             label=f'Target 15% Miss Rate (FA={fa})')
    
    plt.xlabel("False Detection Rate (FDR)")
    plt.ylabel("Miss Rate")
    plt.title("Detection Error Tradeoff (DET) Curve")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plot_path = os.path.join(run_dir, "det_curve.png")
    plt.savefig(plot_path)
    print(f"\n📈 Saved results and DET curve plot to: {run_dir}")


if __name__ == "__main__":
    # Specify the exact folder of the run you want to evaluate
    # Replace the folder name below with your actual dynamically generated timestamp folder
    RUN_TO_EVALUATE = r"saved_models\tiny_crnn_v20260510_181959"  
    
    TEST_DATA_DIR = r"data\wakewords\stop\dataset_split\test"
    
    evaluate_model(RUN_TO_EVALUATE, TEST_DATA_DIR)