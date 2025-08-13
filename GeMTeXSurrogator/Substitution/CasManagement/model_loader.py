import spacy
from sentence_transformers import SentenceTransformer

from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import EMBEDDING_MODEL_NAME
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import EMBEDDING_MODEL_LOCAL_COPY
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import SPACY_MODEL


'''
    todo:
        * Remove it from this place to top hierarchy and send error note!
'''

def load_embedding_model() -> SentenceTransformer:
    if not EMBEDDING_MODEL_LOCAL_COPY.exists():
        download_models()

    print(str(EMBEDDING_MODEL_LOCAL_COPY))

    return SentenceTransformer(str(EMBEDDING_MODEL_LOCAL_COPY))


def download_models() -> None:
    spacy.cli.download(SPACY_MODEL)
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    model.save(EMBEDDING_MODEL_LOCAL_COPY)
