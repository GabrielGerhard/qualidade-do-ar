import unicodedata
from pymongo import MongoClient
import redis

MONGO_URI = "mongodb://localhost:27017"
REDIS_HOST, REDIS_PORT = "localhost", 6379
DB_NOME = "QualidadeAr"
PREFIXO = "qualidadear"

def get_db(nome=DB_NOME):
    return MongoClient(MONGO_URI)[nome]

def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def normaliza(txt):
    """Remove acentos, minúsculas e sem espaços (ex.: 'Chapecó' -> 'chapeco')."""
    sem = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return sem.lower().replace(" ", "")
