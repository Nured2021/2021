"""
Training loop for the GPT language model.
"""

import os
import math
import glob
import time
from typing import Tuple

import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast

from config import ModelConfig, TrainConfig
from model import GPT
from tokenizer import BPETokenizer


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_tokens(path: str, tokenizer: BPETokenizer) -> torch.Tensor:
    """Encodes a plain-text file into a flat 1-D token tensor."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    ids = tokenizer.encode(text, add_bos=False)
    return torch.tensor(ids, dtype=torch.long)


def get_batch(data: torch.Tensor, cfg: TrainConfig, device: str) -> Tuple[torch.Tensor, torch.Tensor]:
    """Samples a random batch of (input, target) token index pairs."""
    ix = torch.randint(len(data) - cfg.context_length, (cfg.batch_size,))
    x = torch.stack([data[i : i + cfg.context_length] for i in ix])
    y = torch.stack([data[i + 1 : i + cfg.context_length + 1] for i in ix])
    return x.to(device), y.to(device)


# ---------------------------------------------------------------------------
# Learning-rate schedule
# ---------------------------------------------------------------------------

def get_lr(step: int, cfg: TrainConfig) -> float:
    """Cosine decay with linear warm-up."""
    if step < cfg.warmup_steps:
        return cfg.learning_rate * step / cfg.warmup_steps
    if step > cfg.max_steps:
        return cfg.min_lr
    decay_ratio = (step - cfg.warmup_steps) / (cfg.max_steps - cfg.warmup_steps)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return cfg.min_lr + coeff * (cfg.learning_rate - cfg.min_lr)


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def save_checkpoint(model: GPT, optimizer: torch.optim.Optimizer, step: int, loss: float, cfg: TrainConfig) -> None:
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    path = os.path.join(cfg.checkpoint_dir, f"ckpt_{step:07d}.pt")
    torch.save({
        "step": step,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": loss,
    }, path)
    print(f"  [ckpt] Saved {path}")

    # Remove old checkpoints beyond keep_last_n
    existing = sorted(glob.glob(os.path.join(cfg.checkpoint_dir, "ckpt_*.pt")))
    for old in existing[: -cfg.keep_last_n]:
        os.remove(old)
        print(f"  [ckpt] Removed {old}")


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@torch.no_grad()
def estimate_val_loss(model: GPT, val_data: torch.Tensor, cfg: TrainConfig, device: str) -> float:
    model.eval()
    losses = []
    for _ in range(cfg.eval_steps):
        x, y = get_batch(val_data, cfg, device)
        with autocast(enabled=cfg.use_amp):
            _, loss = model(x, y)
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def train() -> None:
    tcfg = TrainConfig()
    mcfg = ModelConfig()

    # Device resolution
    if tcfg.device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available – falling back to CPU.")
        tcfg.device = "cpu"
    device = tcfg.device

    torch.manual_seed(tcfg.seed)
    if device == "cuda":
        torch.cuda.manual_seed(tcfg.seed)

    # Tokenizer
    tokenizer = BPETokenizer.load(tcfg.tokenizer_path)
    mcfg.vocab_size = len(tokenizer)
    print(f"Vocabulary size: {mcfg.vocab_size}")

    # Data
    train_data = load_tokens(tcfg.data_path, tokenizer)
    val_data   = load_tokens(tcfg.val_data_path, tokenizer)

    # Model
    model = GPT(mcfg).to(device)
    if tcfg.compile_model and hasattr(torch, "compile"):
        print("Compiling model with torch.compile …")
        model = torch.compile(model)

    # Optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=tcfg.learning_rate,
        betas=tcfg.betas,
        weight_decay=tcfg.weight_decay,
    )
    scaler = GradScaler(enabled=tcfg.use_amp and device == "cuda")

    # Training loop
    model.train()
    t0 = time.time()
    for step in range(1, tcfg.max_steps + 1):
        # Update learning rate
        lr = get_lr(step, tcfg)
        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

        # Gradient accumulation
        optimizer.zero_grad()
        accum_loss = 0.0
        for micro_step in range(tcfg.grad_accum_steps):
            x, y = get_batch(train_data, tcfg, device)
            with autocast(enabled=tcfg.use_amp and device == "cuda"):
                _, loss = model(x, y)
            loss = loss / tcfg.grad_accum_steps
            scaler.scale(loss).backward()
            accum_loss += loss.item()

        # Gradient clipping
        if tcfg.grad_clip > 0.0:
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), tcfg.grad_clip)

        scaler.step(optimizer)
        scaler.update()

        # Logging
        if step % tcfg.log_every == 0:
            elapsed = time.time() - t0
            print(f"step {step:6d} | loss {accum_loss:.4f} | lr {lr:.2e} | {elapsed:.1f}s")
            t0 = time.time()

        # Validation
        if step % tcfg.eval_every == 0:
            val_loss = estimate_val_loss(model, val_data, tcfg, device)
            print(f"  [eval] step {step} | val_loss {val_loss:.4f}")

        # Checkpoint
        if step % tcfg.save_every == 0:
            save_checkpoint(model, optimizer, step, accum_loss, tcfg)

    print("Training complete.")


if __name__ == "__main__":
    train()
