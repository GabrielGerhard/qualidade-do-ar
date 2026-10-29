"""Resumos horários (pipeline do MongoDB) por sensor e por cidade -> Hashes no Redis."""
from datetime import datetime, timedelta, timezone
from config import get_db, get_redis, normaliza, PREFIXO

VALIDA = {k: {"$type": "number"} for k in ["pm25", "pm10", "co2", "temperatura", "umidade"]}
STATS = {"qt_medicoes": {"$sum": 1},
         "pm25_media": {"$avg": "$pm25"}, "pm10_media": {"$avg": "$pm10"}, "co2_media": {"$avg": "$co2"},
         "temperatura_media": {"$avg": "$temperatura"}, "umidade_media": {"$avg": "$umidade"},
         "pm25_max": {"$max": "$pm25"}, "pm10_max": {"$max": "$pm10"}}

def _match(ini, fim):
    return {"$match": {"timestamp": {"$gte": ini, "$lt": fim}, **VALIDA}}

def resumo_sensores(db, ini, fim):
    return list(db.Medicoes.aggregate([_match(ini, fim),
        {"$group": {"_id": "$sensor_id", **STATS}}, {"$sort": {"_id": 1}}]))

def resumo_cidades(db, ini, fim):
    # média global das medições (ponderada), não média das médias dos sensores
    return list(db.Medicoes.aggregate([_match(ini, fim),
        {"$lookup": {"from": "Sensores", "localField": "sensor_id", "foreignField": "_id", "as": "s"}},
        {"$unwind": "$s"},
        {"$group": {"_id": {"uf": "$s.localizacao.uf", "cidade": "$s.localizacao.cidade"}, **STATS}},
        {"$sort": {"_id.cidade": 1}}]))

def _hash(doc, ini, fim):
    h = {"inicio_periodo": ini.strftime("%Y-%m-%dT%H:%M:%SZ"), "fim_periodo": fim.strftime("%Y-%m-%dT%H:%M:%SZ")}
    for k, v in doc.items():
        if k != "_id":
            h[k] = round(v, 2) if isinstance(v, float) else v
    return h

def atualizar_redis(db, r, ini, prefixo=PREFIXO):
    fim = ini + timedelta(hours=1)
    chaves = []
    for d in resumo_sensores(db, ini, fim):
        ch = f"{prefixo}:sensor:{d['_id']}"
        r.delete(ch); r.hset(ch, mapping=_hash(d, ini, fim)); chaves.append(ch)
    for d in resumo_cidades(db, ini, fim):
        ch = f"{prefixo}:cidade:{d['_id']['uf']}:{normaliza(d['_id']['cidade'])}"
        r.delete(ch); r.hset(ch, mapping=_hash(d, ini, fim)); chaves.append(ch)
    return chaves

if __name__ == "__main__":
    ini = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    for ch in atualizar_redis(get_db(), get_redis(), ini):
        print("OK", ch)
