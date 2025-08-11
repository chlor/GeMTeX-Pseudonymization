import spacy
from sentence_transformers import SentenceTransformer

from GeMTeXSurrogator.Substitution.CASmanagement.const import EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_LOCAL_COPY, \
    SPACY_MODEL


def load_embedding_model() -> SentenceTransformer:
    if not EMBEDDING_MODEL_LOCAL_COPY.exists():
        download_models()
    return SentenceTransformer(str(EMBEDDING_MODEL_LOCAL_COPY))


def download_models() -> None:
    spacy.cli.download(SPACY_MODEL)
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    model.save(EMBEDDING_MODEL_LOCAL_COPY)
