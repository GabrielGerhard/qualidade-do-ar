"""Teste com dados DIFERENTES dos de produção: banco 'QualidadeArTeste' e prefixo Redis 'teste:qualidadear'."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timezone
from config import get_db, get_redis, normaliza
from agregacao import atualizar_redis
from consultas import medicoes_sensor, mostrar_hashes

PFX = "teste:qualidadear"
T = lambda h, m: datetime(2026, 11, 1, h, m, tzinfo=timezone.utc)
db, r = get_db("QualidadeArTeste"), get_redis()
db.Sensores.drop(); db.Medicoes.drop()
for ch in r.scan_iter(f"{PFX}:*"): r.delete(ch)

db.Sensores.insert_many([
    {"_id": "T01", "localizacao": {"cidade": "Florianópolis", "uf": "SC"}},
    {"_id": "T02", "localizacao": {"cidade": "Florianópolis", "uf": "SC"}}])
m = lambda s, t, pm25: {"sensor_id": s, "timestamp": t, "pm25": pm25, "pm10": (None if pm25 is None else pm25 * 2),
                        "co2": 500, "temperatura": 20.0, "umidade": 60}
db.Medicoes.insert_many([
    m("T01", T(8, 0), 10), m("T01", T(8, 5), 20),                    # média 15
    *[m("T02", T(8, 10 + 5 * i), 30) for i in range(4)],             # média 30
    {**m("T01", T(8, 30), None)},                                    # inválida (ignorada)
    m("T01", T(9, 0), 999)])                                         # fora da janela

atualizar_redis(db, r, T(8, 0), prefixo=PFX)
cid = r.hgetall(f"{PFX}:cidade:SC:{normaliza('Florianópolis')}")
s1 = r.hgetall(f"{PFX}:sensor:T01")

assert normaliza("Florianópolis") == "florianopolis"
assert int(cid["qt_medicoes"]) == 6, cid
assert float(cid["pm25_media"]) == 25.0, "média global (150/6) != média das médias (22.5)"
assert float(cid["pm25_max"]) == 30.0
assert int(s1["qt_medicoes"]) == 2 and float(s1["pm25_media"]) == 15.0
assert len(medicoes_sensor(db, "T02", T(8, 0), T(9, 0))) == 4
print("TODOS OS TESTES PASSARAM")
mostrar_hashes(r, PFX)
