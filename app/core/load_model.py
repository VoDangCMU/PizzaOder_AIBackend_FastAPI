from langchain_community.llms.ctransformers import CTransformers
from sentence_transformers import SentenceTransformer


llm_instance = None
embedding_model_instance = None




def get_embedding_model():
    global embedding_model_instance
    if embedding_model_instance is None:
        model_name = "hothanhtienqb/mind_map_blog_model"
        try:
            print(f"Đang tải mô hình embedding: {model_name}")
            embedding_model_instance = SentenceTransformer(model_name)
            print("Mô hình embedding đã được tải thành công.")
        except Exception as e:
            print(f"Lỗi khi tải mô hình embedding: {e}")
            return None
    return embedding_model_instance
