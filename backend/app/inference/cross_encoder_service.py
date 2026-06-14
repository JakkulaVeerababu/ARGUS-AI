from typing import List, Tuple
import numpy as np
from backend.app.inference.model_manager import ModelManager


class CrossEncoderService:
    def __init__(self, model_name: str = "ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.manager = ModelManager()
        self.session = None
        self.tokenizer = None

    def _ensure_loaded(self):
        if self.session is None or self.tokenizer is None:
            self.session, self.tokenizer = self.manager.get_model_and_tokenizer(
                self.model_name
            )

    def score_pairs(
        self, pairs: List[Tuple[str, str]], batch_size: int = 32
    ) -> List[float]:
        """
        Scores query-document pairs using the ONNX model.
        Input format: [(query, doc_text), (query, doc_text), ...]
        Returns a list of float scores.
        """
        self._ensure_loaded()
        if not pairs:
            return []

        all_scores = []

        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i : i + batch_size]

            queries = [p[0] for p in batch_pairs]
            docs = [p[1] for p in batch_pairs]

            # Tokenize pairs together
            encoded_inputs = self.tokenizer(
                queries,
                docs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="np",
            )

            # Prepare inputs for ONNX session
            onnx_inputs = {}
            for input_meta in self.session.get_inputs():
                name = input_meta.name
                if name in encoded_inputs:
                    onnx_inputs[name] = encoded_inputs[name].astype(np.int64)
                elif name == "token_type_ids":
                    # Fallback if tokenizer did not produce token_type_ids
                    onnx_inputs[name] = np.zeros_like(
                        encoded_inputs["input_ids"], dtype=np.int64
                    )

            # Run inference
            outputs = self.session.run(None, onnx_inputs)

            # Sequence classification output logits is the first element
            logits = outputs[0]

            # Squeeze scores if shape is [B, 1]
            if len(logits.shape) > 1 and logits.shape[1] == 1:
                batch_scores = logits.squeeze(axis=1).tolist()
            else:
                batch_scores = logits.tolist()

            all_scores.extend(batch_scores)

        return [float(s) for s in all_scores]
