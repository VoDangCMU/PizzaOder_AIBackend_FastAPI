# app/services/prediction_service.py
import joblib
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download

classifier_path = hf_hub_download(repo_id="hothanhtienqb/sentiment_logistic_regression_model", filename="logistic_regression_model.pkl")
classifier = joblib.load(classifier_path)
# classifier = joblib.load('C:\\Users\\Admin\\Desktop\\New folder\\New folder\\MindMap\\logistic_regression_model.pkl')
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

label_mapping = {'love': 0, 'sadness': 1, 'joy': 2, 'anger': 3, 'fear': 4, 'surprise': 5}
reverse_label_mapping = {v: k for k, v in label_mapping.items()}

def predict_emotion(sentence: str):
    embedding = model.encode(sentence, convert_to_tensor=True)
    embedding = embedding.cpu().detach().numpy().reshape(1, -1)
    predicted_class = classifier.predict(embedding)[0]
    return reverse_label_mapping[predicted_class]
