from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
import nltk

stop_words = set(stopwords.words('english'))
def clean_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()
    text = re.sub(r"[^\w\s.,!?;:]", "", text)

    return text