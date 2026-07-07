"""
Configuration module for the GPT model and training loop.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ModelConfig:
    """GPT architecture parameters."""
    vocab_size: int = 50257       # Overwritten automatically by the tokenizer size
    context_length: int = 512     # Maximum sequence length (block_size)
    n_embd: int = 384             # Embedding dimension
    n_head: int = 6               # Number of attention heads (n_embd % n_head must be 0)
    n_layer: int = 6              # Number of Transformer blocks
    dropout: float = 0.1          # Dropout probability across layers


@dataclass
class TrainConfig:
    """Hyperparameters for the training run."""
    # Data & Path configurations
    data_path: str = "data/train.txt"
    val_data_path: str = "data/val.txt"
    tokenizer_path: str = "tokenizer.json"
    checkpoint_dir: str = "checkpoints"

    # Optimization parameters
    max_steps: int = 5000
    batch_size: int = 16
    grad_accum_steps: int = 4     # Total effective batch size = batch_size * grad_accum_steps
    learning_rate: float = 6e-4
    min_lr: float = 6e-5          # Final decay target for the Cosine schedule
    warmup_steps: int = 200
    weight_decay: float = 0.1
    betas: Tuple[float, float] = (0.9, 0.95)
    grad_clip: float = 1.0

    # Performance & Framework features
    use_amp: bool = True          # Automatic Mixed Precision
    compile_model: bool = True    # Replaces graph overhead via torch.compile (PyTorch >= 2.0)
    device: str = "cuda"          # Fallback automatically managed in train.py
    seed: int = 1337

    # Logging and saving cadences
    log_every: int = 10
    eval_every: int = 100
    eval_steps: int = 20          # Micro-steps to average out valuation loss
    save_every: int = 500
    keep_last_n: int = 3          # Max number of physical checkpoints retained on disk
