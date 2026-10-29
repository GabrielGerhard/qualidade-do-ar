"""Consulta por sensor e intervalo no MongoDB e exibição dos Hashes do Redis no console."""
from datetime import datetime, timezone
from config import get_db, get_redis, PREFIXO

def medicoes_sensor(db, sensor_id, ini, fim):
    return list(db.Medicoes.find({"sensor_id": sensor_id, "timestamp": {"$gte": ini, "$lt": fim}}).sort("timestamp", 1))

def mostrar_hashes(r, prefixo=PREFIXO):
    for ch in sorted(r.scan_iter(f"{prefixo}:*")):
        print(f"\n{ch}")
        for k, v in r.hgetall(ch).items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    ini = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    fim = datetime(2026, 10, 20, 11, 0, tzinfo=timezone.utc)
    ms = medicoes_sensor(get_db(), "S001", ini, fim)
    print(f"S001 entre {ini:%H:%M} e {fim:%H:%M} UTC: {len(ms)} medições")
    for m in ms[:3]:
        print(" ", m["timestamp"], m["pm25"], m["pm10"], m["co2"])
    mostrar_hashes(get_redis())
