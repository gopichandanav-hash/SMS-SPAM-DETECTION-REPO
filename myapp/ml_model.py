import pickle
import re
import string
from pathlib import Path

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.sequence import pad_sequences
except Exception:  # pragma: no cover - fallback for environments without TensorFlow
    load_model = None
    pad_sequences = None

try:
    from googletrans import Translator
except Exception:  # pragma: no cover - fallback when the package is unavailable
    Translator = None

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "lstm_spam_model.keras"
TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

MODEL = None
TOKENIZER = None
LOAD_FAILURE = None

try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    try:
        nltk.download("stopwords", quiet=True)
        STOP_WORDS = set(stopwords.words("english"))
    except Exception:
        STOP_WORDS = {
            "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
            "had", "has", "have", "he", "her", "here", "hers", "him", "his", "i", "in",
            "into", "is", "it", "its", "me", "my", "of", "on", "or", "our", "ours",
            "she", "that", "the", "their", "them", "there", "these", "they", "this",
            "those", "to", "was", "were", "what", "when", "where", "which", "who",
            "whom", "why", "will", "with", "you", "your", "yours"
        }

STEMMER = PorterStemmer()
MAX_LENGTH = 100

translator = Translator() if Translator is not None else None


def _load_model_and_tokenizer():
    global MODEL, TOKENIZER, LOAD_FAILURE
    import tensorflow as tf
    import keras

    print("TensorFlow:", tf.__version__)
    print("Keras:", keras.__version__)
    if MODEL is not None and TOKENIZER is not None:
        return MODEL, TOKENIZER

    if LOAD_FAILURE is not None:
        return MODEL, TOKENIZER

    if load_model is not None and MODEL_PATH.exists():
        try:
            MODEL = load_model(MODEL_PATH)
        except Exception as exc:
            LOAD_FAILURE = exc
            MODEL = None
            print(f"Unable to load Keras model: {exc}")

    if TOKENIZER is None and TOKENIZER_PATH.exists():
        try:
            with TOKENIZER_PATH.open("rb") as handle:
                TOKENIZER = pickle.load(handle)
        except Exception as exc:
            if LOAD_FAILURE is None:
                LOAD_FAILURE = exc
            TOKENIZER = None
            print(f"Unable to load tokenizer: {exc}")

    return MODEL, TOKENIZER


def translate_to_english(text):
    if translator is None:
        return text

    try:
        return translator.translate(text, dest="en").text
    except Exception:
        return text


def preprocess(text):
    text = str(text).lower()

    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))

    words = text.split()
    words = [STEMMER.stem(word) for word in words if word not in STOP_WORDS]

    return " ".join(words)


def predict_sms(body):
    model, tokenizer = _load_model_and_tokenizer()

    if model is None or tokenizer is None or pad_sequences is None:
        return "ham"

    try:
        translated = translate_to_english(body)
        cleaned = preprocess(translated)

        sequence = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(
            sequence,
            maxlen=MAX_LENGTH,
            padding="post",
            truncating="post"
        )

        pred = model.predict(padded, verbose=0)[0][0]
    except Exception as exc:
        print(f"Prediction fallback triggered: {exc}")
        return "ham"

    if pred >= 0.5:
        return "spam"

    return "ham"
