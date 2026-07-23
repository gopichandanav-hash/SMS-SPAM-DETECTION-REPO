import re
import pickle
import string

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from googletrans import Translator

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download("stopwords", quiet=True)

MODEL = load_model("lstm_spam_model.keras")

with open("lstm_tokenizer.pkl", "rb") as f:
    TOKENIZER = pickle.load(f)

translator = Translator()

STOP_WORDS = set(stopwords.words("english"))
STEMMER = PorterStemmer()

MAX_LENGTH = 100


def translate_to_english(text):
    try:
        return translator.translate(text, dest="en").text
    except Exception:
        return text


def preprocess(text):
    text = str(text).lower()

    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    text = text.translate(str.maketrans('', '', string.punctuation))

    # Punctuation has already been removed, so whitespace tokenization is
    # sufficient here.  ``word_tokenize`` additionally requires NLTK's punkt
    # (and, on newer NLTK versions, punkt_tab) data files at runtime.
    words = text.split()

    words = [
        STEMMER.stem(word)
        for word in words
        if word not in STOP_WORDS
    ]

    return " ".join(words)


def predict_sms(body):

    translated = translate_to_english(body)

    cleaned = preprocess(translated)

    sequence = TOKENIZER.texts_to_sequences([cleaned])

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post"
    )

    pred = MODEL.predict(padded, verbose=0)[0][0]

    if pred >= 0.5:
        return "spam"

    return "ham"
