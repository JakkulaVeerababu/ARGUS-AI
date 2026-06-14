import numpy as np
from typing import List, Union
from backend.app.inference.model_manager import ModelManager


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.manager = ModelManager()
        self.session = None
        self.tokenizer = None

    def _ensure_loaded(self):
        if self.session is None or self.tokenizer is None:
            self.session, self.tokenizer = self.manager.get_model_and_tokenizer(
                self.model_name
            )

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 64,
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        """
        Generates dense vector embeddings using the ONNX model.
        Args:
            texts: A single text or list of texts.
            batch_size: Batch size for inference.
            normalize_embeddings: Whether to L2 normalize embeddings.
        Returns:
            A numpy array of shape (N, 384) representing the dense embeddings.
        """
        self._ensure_loaded()

        is_single_text = isinstance(texts, str)
        if is_single_text:
            texts = [texts]

        if not texts:
            empty_emb = np.empty((0, 384), dtype=np.float32)
            return empty_emb[0] if is_single_text else empty_emb

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]

            # Tokenize batch
            encoded_inputs = self.tokenizer(
                batch_texts,
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

            # token_embeddings (last_hidden_state) is always the first output
            token_embeddings = outputs[0]
            attention_mask = encoded_inputs["attention_mask"]

            # Perform mean pooling
            input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
            sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
            sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
            batch_embeddings = sum_embeddings / sum_mask

            if normalize_embeddings:
                norms = np.linalg.norm(batch_embeddings, ord=2, axis=1, keepdims=True)
                norms = np.clip(norms, a_min=1e-9, a_max=None)
                batch_embeddings = batch_embeddings / norms

            all_embeddings.append(batch_embeddings)

        stacked = np.vstack(all_embeddings)
        return stacked[0] if is_single_text else stacked
