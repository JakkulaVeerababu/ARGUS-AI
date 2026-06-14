import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app.preprocessing.candidate_loader import CandidateLoader

class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", output_path: str = None):
        self.model_name = model_name
        self.output_path = output_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../artifacts/candidate_embeddings.npy")
        )
        self.model = None

    def load_model(self):
        """Loads the SentenceTransformer model on CPU."""
        if self.model is None:
            print(f"Loading SentenceTransformer model '{self.model_name}' on CPU...")
            start_time = time.time()
            # Force CPU execution per challenge rules
            self.model = SentenceTransformer(self.model_name, device="cpu")
            print(f"Model loaded in {time.time() - start_time:.2f} seconds.")

    def generate_and_save(self, candidates_file: str = None, batch_size: int = 512):
        """
        Streams candidate documents, generates dense 384-dimensional embeddings
        in batches, L2-normalizes them, and saves the final matrix as a NumPy array.
        """
        self.load_model()
        
        loader = CandidateLoader(candidates_file)
        print("Starting candidate streaming and embedding generation...")
        
        embeddings_list = []
        candidate_ids = []
        batch_docs = []
        batch_ids = []
        
        start_time = time.time()
        count = 0
        
        for cand in loader.stream_candidates():
            cid = cand.get("candidate_id")
            doc = cand.get("document_text", "")
            
            batch_docs.append(doc)
            batch_ids.append(cid)
            count += 1
            
            if len(batch_docs) >= batch_size:
                # Encode and L2 normalize for cosine similarity inner product
                batch_embs = self.model.encode(
                    batch_docs,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                embeddings_list.append(batch_embs)
                candidate_ids.extend(batch_ids)
                
                batch_docs = []
                batch_ids = []
                
                if count % 10000 == 0:
                    elapsed = time.time() - start_time
                    rate = count / elapsed
                    print(f"Processed {count} candidates... Elapsed: {elapsed:.1f}s ({rate:.1f} cand/s)")
        
        # Process remaining candidates in the last batch
        if batch_docs:
            batch_embs = self.model.encode(
                batch_docs,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            embeddings_list.append(batch_embs)
            candidate_ids.extend(batch_ids)
            
        # Concatenate all batches
        print("Concatenating embedding batches...")
        all_embeddings = np.vstack(embeddings_list)
        
        # Save embeddings matrix
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        np.save(self.output_path, all_embeddings)
        print(f"Saved {all_embeddings.shape[0]} embeddings to: {self.output_path}")
        print(f"Embedding shape: {all_embeddings.shape}")
        
        # Also save candidate IDs to preserve mapping order
        ids_path = self.output_path.replace("candidate_embeddings.npy", "candidate_ids.pkl")
        import pickle
        with open(ids_path, "wb") as f:
            pickle.dump(candidate_ids, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved matching candidate IDs mapping to: {ids_path}")
        print(f"Total time elapsed: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    generator = EmbeddingGenerator()
    try:
        # Run a small limit test or full generation
        # Limit argument is handled by custom stream/load if needed, but here we run full generator
        generator.generate_and_save()
    except Exception as e:
        print(f"Error: {e}")
