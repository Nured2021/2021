"""
Core GPT Transformer architecture implementation.
"""

import math
from typing import Optional

import torch
import torch.nn as nn
from torch.nn import functional as F

from config import ModelConfig


class CausalSelfAttention(nn.Module):
    """
    Standard multi-head causal self-attention with a projection layer.
    """
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0, "n_embd must be divisible by n_head"

        # Key, query, value projections for all heads packaged into one linear layer
        self.c_attn = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=False)
        # Output projection
        self.c_proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=False)

        # Regularization
        self.attn_dropout = nn.Dropout(cfg.dropout)
        self.resid_dropout = nn.Dropout(cfg.dropout)

        self.n_head = cfg.n_head
        self.n_embd = cfg.n_embd

        # Causal mask register (lower triangular matrix)
        self.register_buffer(
            "bias",
            torch.tril(torch.ones(cfg.context_length, cfg.context_length))
            .view(1, 1, cfg.context_length, cfg.context_length)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.size()  # Batch size, sequence length, embedding channels

        # Calculate query, key, values for all heads in batch
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)

        # Reshape to (B, n_head, T, head_size)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)

        # Scaled dot-product attention
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        # Enforce causality by filling upper triangle with -inf
        att = att.masked_fill(self.bias[:, :, :T, :T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)

        y = att @ v  # (B, n_head, T, T) x (B, n_head, T, head_size) -> (B, n_head, T, head_size)
        y = y.transpose(1, 2).contiguous().view(B, T, C)  # Re-assemble head outputs side-by-side

        # Output projection
        y = self.resid_dropout(self.c_proj(y))
        return y


class MLP(nn.Module):
    """
    Position-wise Feed-Forward Network using GeLU activation.
    """
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.c_fc   = nn.Linear(cfg.n_embd, 4 * cfg.n_embd, bias=False)
        self.gelu   = nn.GELU()
        self.c_proj = nn.Linear(4 * cfg.n_embd, cfg.n_embd, bias=False)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.c_fc(x)
        x = self.gelu(x)
        x = self.c_proj(x)
        x = self.dropout(x)
        return x


class Block(nn.Module):
    """
    An isolated Transformer layer mapping sequence tensors to sequence tensors.
    """
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.ln_1 = nn.LayerNorm(cfg.n_embd)
        self.attn = CausalSelfAttention(cfg)
        self.ln_2 = nn.LayerNorm(cfg.n_embd)
        self.mlp = MLP(cfg)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-normalization layout with skip-connections
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class GPT(nn.Module):
    """
    The full Autoregressive Language Model container.
    """
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.cfg = cfg

        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(cfg.vocab_size, cfg.n_embd),
            wpe = nn.Embedding(cfg.context_length, cfg.n_embd),
            drop = nn.Dropout(cfg.dropout),
            h = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)]),
            ln_f = nn.LayerNorm(cfg.n_embd),
        ))
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)

        # Weight sharing / tying across token embeddings and output projections
        self.transformer.wte.weight = self.lm_head.weight

        # Initialize all weights uniformly
        self.apply(self._init_weights)
        print(f"Total model parameters: {self.get_num_params():,}")

    def get_num_params(self) -> int:
        """Returns physical parameter count excluding weight-tied components."""
        n_params = sum(p.numel() for p in self.parameters())
        # Deduct tied token embedding weight space
        n_params -= self.transformer.wte.weight.numel()
        return n_params

    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx: torch.Tensor, targets: Optional[torch.Tensor] = None):
        device = idx.device
        _, t = idx.size()
        assert t <= self.cfg.context_length, (
            f"Cannot forward sequence of length {t}, context length block is {self.cfg.context_length}"
        )

        # Forward token and position embeddings
        pos = torch.arange(0, t, dtype=torch.long, device=device)
        tok_emb = self.transformer.wte(idx)  # (B, T, n_embd)
        pos_emb = self.transformer.wpe(pos)  # (1, T, n_embd)

        x = self.transformer.drop(tok_emb + pos_emb)

        # Traverse individual transformer blocks
        for block in self.transformer.h:
            x = block(x)

        x = self.transformer.ln_f(x)

        if targets is not None:
            # Full loss evaluating forward pass
            logits = self.lm_head(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-1)
            return logits, loss
        else:
            # Evaluation/inference mode optimized shortcut
            logits = self.lm_head(x[:, [-1], :])  # Focus output on the absolute latest sequence position
            return logits, None

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int, temperature: float = 1.0, top_k: Optional[int] = None) -> torch.Tensor:
        """
        Autoregressive generation loop taking token histories and appending novel generations.
        """
        for _ in range(max_new_tokens):
            # Crop inputs if context history exceeds limits
            idx_cond = idx if idx.size(1) <= self.cfg.context_length else idx[:, -self.cfg.context_length:]
            logits, _ = self(idx_cond)

            # Extract final step logits and scale via temperature
            logits = logits[:, -1, :] / temperature

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('inf')

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)

        return idx
