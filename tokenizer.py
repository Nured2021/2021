"""
Minimal Byte-Pair Encoding (BPE) Tokenizer interface using Hugging Face tokenizers.
"""

from __future__ import annotations
import os
from typing import List

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace


class BPETokenizer:
    def __init__(self, vocab_size: int = 50257):
        # We model GPT-2 style BPE structures beginning with baseline components
        self.tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
        self.tokenizer.pre_tokenizer = Whitespace()
        self.vocab_size = vocab_size

    def train(self, files: List[str]) -> None:
        """Trains a new BPE tokenizer structure on raw plain text file blocks."""
        trainer = BpeTrainer(
            vocab_size=self.vocab_size,
            special_tokens=["[UNK]", "[BOS]", "[EOS]", "[PAD]"]
        )
        self.tokenizer.train(files, trainer)

    def save(self, path: str) -> None:
        """Saves compiled configuration down to local path JSON files."""
        self.tokenizer.save(path)

    @classmethod
    def load(cls, path: str) -> BPETokenizer:
        """Loads static pre-compiled local configuration JSON objects."""
        instance = cls()
        instance.tokenizer = Tokenizer.from_file(path)
        return instance

    def encode(self, text: str, add_bos: bool = True) -> List[int]:
        output = self.tokenizer.encode(text)
        ids = output.ids
        if add_bos:
            # Map dynamic BOS sequence tokens if present in training profile
            bos_id = self.tokenizer.token_to_id("[BOS]")
            if bos_id is not None:
                ids = [bos_id] + ids
        return ids

    def decode(self, ids: List[int]) -> str:
        return self.tokenizer.decode(ids)

    def __len__(self) -> int:
        return self.tokenizer.get_vocab_size()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train a text tokenizer configuration")
    parser.add_argument("input_file", type=str, help="Path to input text data file (e.g. data/train.txt)")
    parser.add_argument("output_path", type=str, default="tokenizer.json", help="Destination path for json layout")
    args = parser.parse_args()

    print(f"Beginning training protocol for tokenizer on {args.input_file}...")
    tk = BPETokenizer()
    tk.train([args.input_file])
    tk.save(args.output_path)
    print(f"Saved completed tokenization schema to {args.output_path} | Vocab Size: {len(tk)}")
