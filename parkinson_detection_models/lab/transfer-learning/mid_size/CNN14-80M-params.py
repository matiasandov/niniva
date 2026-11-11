import librosa
import numpy as np
from panns_inference import AudioTagging, labels

def run_cnn14(audio_path):
    print(f"Loading audio file: {audio_path}...")
    
    # 1. Load the audio file
    # PANNs CNN14 expects a sample rate of 32,000 Hz and mono audio
    audio, _ = librosa.load(audio_path, sr=32000, mono=True)
    
    # Add a batch dimension: shape becomes (1, segment_samples)
    audio = audio[None, :] 

    print("Initializing CNN14 model...")
    # 2. Initialize the model
    # checkpoint_path=None forces the library to automatically download 
    # the 'Cnn14_mAP=0.431.pth' weights to your local home directory (~/.panns_data).
    # Change device to 'cuda' if you have an NVIDIA GPU configured.
    device = 'cpu' 
    at = AudioTagging(checkpoint_path=None, device=device)

    print("Running inference...")
    # 3. Run inference
    # clipwise_output contains the probabilities for the 527 AudioSet classes
    # embedding contains the 2048-dimensional feature vector from the penultimate layer
    (clipwise_output, embedding) = at.inference(audio)

    # 4. Display the top 5 predicted sound tags
    print("\n--- Top 5 Predictions ---")
    top_indices = np.argsort(clipwise_output[0])[::-1][:5]
    
    for idx in top_indices:
        class_name = labels[idx]
        probability = clipwise_output[0][idx]
        print(f"{class_name:<25}: {probability:.4f}")

if __name__ == "__main__":
    # Replace this with the path to any standard .wav or .mp3 file on your machine
    sample_audio = "data\audio_data\sounds\fold1\7061-6-0-0.wav" 
    
    try:
        run_cnn14(sample_audio)
    except FileNotFoundError:
        print(f"Error: Could not find '{sample_audio}'. Please provide a valid audio file.")