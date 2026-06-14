import os
from optimum.onnxruntime import (
    ORTModelForFeatureExtraction,
    ORTModelForSequenceClassification,
)
from transformers import AutoTokenizer


def export_models():
    # Define directory paths relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.abspath(os.path.join(current_dir, "../../../models"))

    # 1. Export sentence-transformers/all-MiniLM-L6-v2
    emb_model_id = "sentence-transformers/all-MiniLM-L6-v2"
    emb_export_path = os.path.join(models_dir, "all-MiniLM-L6-v2")

    print(f"Ensuring model directory exists: {models_dir}")
    os.makedirs(models_dir, exist_ok=True)

    if not os.path.exists(os.path.join(emb_export_path, "model.onnx")):
        print(f"Exporting {emb_model_id} to ONNX...")
        tokenizer = AutoTokenizer.from_pretrained(emb_model_id)
        model = ORTModelForFeatureExtraction.from_pretrained(emb_model_id, export=True)
        model.save_pretrained(emb_export_path)
        tokenizer.save_pretrained(emb_export_path)
        print(f"Successfully exported {emb_model_id} to {emb_export_path}")
    else:
        print(f"ONNX model for {emb_model_id} already exists at {emb_export_path}")

    # 2. Export cross-encoder/ms-marco-MiniLM-L-6-v2
    ce_model_id = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ce_export_path = os.path.join(models_dir, "ms-marco-MiniLM-L-6-v2")

    if not os.path.exists(os.path.join(ce_export_path, "model.onnx")):
        print(f"Exporting {ce_model_id} to ONNX...")
        tokenizer = AutoTokenizer.from_pretrained(ce_model_id)
        model = ORTModelForSequenceClassification.from_pretrained(
            ce_model_id, export=True
        )
        model.save_pretrained(ce_export_path)
        tokenizer.save_pretrained(ce_export_path)
        print(f"Successfully exported {ce_model_id} to {ce_export_path}")
    else:
        print(f"ONNX model for {ce_model_id} already exists at {ce_export_path}")


if __name__ == "__main__":
    export_models()
