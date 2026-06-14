import os
import time
import numpy as np
import faiss

class FaissIndexBuilder:
    def __init__(self, embeddings_path: str = None, index_path: str = None):
        self.embeddings_path = embeddings_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../artifacts/candidate_embeddings.npy")
        )
        self.index_path = index_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../artifacts/faiss_index.bin")
        )

    def build_and_save(self):
        """Loads candidate embeddings, builds a FAISS index, and saves it."""
        if not os.path.exists(self.embeddings_path):
            raise FileNotFoundError(f"Embeddings file not found at: {self.embeddings_path}")
            
        print(f"Loading candidate embeddings from: {self.embeddings_path}...")
        start_time = time.time()
        embeddings = np.load(self.embeddings_path)
        print(f"Loaded embeddings of shape {embeddings.shape} in {time.time() - start_time:.2f} seconds.")
        
        num_candidates, dimension = embeddings.shape
        
        print(f"Initializing FAISS IndexFlatIP (Flat Inner Product) index for dimension {dimension}...")
        # IndexFlatIP with unit vectors calculates Cosine Similarity
        index = faiss.IndexFlatIP(dimension)
        
        # Verify alignment and float32 type
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
            
        # Add to index
        print("Adding candidate vectors to the FAISS index...")
        index.add(embeddings)
        print(f"FAISS index populated. Total vectors: {index.ntotal}")
        
        # Save index
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(index, self.index_path)
        print(f"FAISS index successfully saved to: {self.index_path}")
        print(f"Index creation completed in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    builder = FaissIndexBuilder()
    try:
        builder.build_and_save()
    except Exception as e:
        print(f"Error: {e}")
