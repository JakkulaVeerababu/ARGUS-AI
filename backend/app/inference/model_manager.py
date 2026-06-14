import os
import threading
import onnxruntime as ort
from transformers import AutoTokenizer

class ModelManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            
            # Setup paths relative to root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.models_dir = os.path.abspath(os.path.join(current_dir, "../../../models"))
            
            self.sessions = {}
            self.tokenizers = {}
            self.load_lock = threading.Lock()

    def get_model_and_tokenizer(self, model_name_or_dir: str):
        """
        Retrieves tokenizer and ONNX inference session for a model.
        Loads it lazily and thread-safely if not already loaded.
        """
        with self.load_lock:
            if model_name_or_dir in self.sessions:
                return self.sessions[model_name_or_dir], self.tokenizers[model_name_or_dir]
                
            # Check if model exists in models_dir as a directory containing model.onnx
            model_path = os.path.join(self.models_dir, model_name_or_dir)
            onnx_path = os.path.join(model_path, "model.onnx")
            
            if not os.path.exists(onnx_path):
                # Attempt to run onnx_converter programmatically if files are missing
                from backend.app.inference.onnx_converter import export_models
                print(f"ONNX model file not found at {onnx_path}. Triggering conversion...")
                export_models()
                
            if not os.path.exists(onnx_path):
                raise FileNotFoundError(f"Failed to load/convert ONNX model at: {onnx_path}")
                
            print(f"Loading ONNX InferenceSession for '{model_name_or_dir}' from: {onnx_path}")
            
            # Optimize session settings for multi-threaded CPU execution
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 4
            sess_options.inter_op_num_threads = 4
            sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            session = ort.InferenceSession(onnx_path, sess_options, providers=["CPUExecutionProvider"])
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            self.sessions[model_name_or_dir] = session
            self.tokenizers[model_name_or_dir] = tokenizer
            
            return session, tokenizer
