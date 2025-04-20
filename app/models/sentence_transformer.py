from sentence_transformers import SentenceTransformer

def load_model(model_path):
    model = SentenceTransformer(model_path)
    return model