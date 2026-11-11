from src.models.tiny_crnn import TinyCRNN


def build_crnn_58k():
    """CRNN-58k with 20-bin LFBE features (50k budget)."""
    return TinyCRNN(
        n_mels=20,
        n_frames=100,
        conv_channels=(32, 32, 32),
        conv_kernels=((5, 5), (5, 3), (10, 3)),
        conv_strides=((1, 1), (2, 1), (1, 1)),
        gru_hidden=32,
        fc_hidden=32,
        num_classes=2,
    )


def build_crnn_89k():
    """CRNN-89k with 20-bin LFBE features (50k budget)."""
    return TinyCRNN(
        n_mels=20,
        n_frames=100,
        conv_channels=(48, 48, 48),
        conv_kernels=((5, 5), (5, 3), (10, 3)),
        conv_strides=((1, 1), (2, 1), (1, 1)),
        gru_hidden=48,
        fc_hidden=48,
        num_classes=2,
    )