import torch

from src.models.lower_params_crnn import build_crnn_58k, build_crnn_89k
from src.models.tiny_crnn import TinyCRNN, count_parameters
from src.models.delta_variant_tiny_crnn import DeltaLFBETinyCRNN
from src.streaming import HighDimStreamingGRU, ParallelStreamingCRNN


if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # ---- Build CRNN-239k (250k budget) ----
    model_239k = TinyCRNN(
        n_mels=64, n_frames=100,
        conv_channels=(64, 64, 64),
        conv_kernels=((5, 5), (5, 5), (10, 4)),
        conv_strides=((1, 2), (2, 2), (1, 1)),
        gru_hidden=64, fc_hidden=64,
        use_attention=True,
    )
    print(f"CRNN-239k params: {count_parameters(model_239k):,}")
    print(f"  T' (time steps to GRU) : {model_239k.t_out}")
    print(f"  feat dim (f'*c')       : {model_239k.feat_dim}")

    x = torch.randn(4, 1, 100, 64)
    print("Output shape:", model_239k(x).shape)

    # ---- Delta-LFBE variant ----
    model_delta = DeltaLFBETinyCRNN(n_mels=64, n_frames=101)
    x101 = torch.randn(4, 1, 101, 64)
    print("Delta-LFBE output:", model_delta(x101).shape)

    # ---- 50k budget models ----
    print(f"CRNN-58k params : {count_parameters(build_crnn_58k()):,}")
    print(f"CRNN-89k params : {count_parameters(build_crnn_89k()):,}")

    # ---- Streaming with parallel decoders ----
    streamer = ParallelStreamingCRNN(model_239k)
    fake_conv_step = torch.randn(1, model_239k.feat_dim)
    for i in range(25):
        post = streamer.step(fake_conv_step)
        if post is not None:
            print(f"step {i}: posterior shape {post.shape}")

    # ---- High-dim streaming GRU ----
    hd_gru = HighDimStreamingGRU(model_239k.gru, t_prime=model_239k.t_out)
    win = torch.randn(1, 2 * model_239k.t_out - 1, model_239k.feat_dim)
    print("High-dim GRU output:", hd_gru(win).shape)