"""Cadastra 6 sensores em 3 cidades e gera 24 h de medições a cada 5 min
(288 por sensor x 6 = 1.728 documentos)."""
import random
from datetime import datetime, timedelta, timezone
from config import get_db

GRANDEZAS = ["PM2.5", "PM10", "CO2", "temperatura", "umidade"]
SENSORES = [
    ("S001", "Centro", "Chapecó", "SC", -27.1009, -52.6157),
    ("S002", "Zona norte", "Chapecó", "SC", -27.0748, -52.6240),
    ("S003", "Centro", "Xanxerê", "SC", -26.8770, -52.4040),
    ("S004", "Bairro industrial", "Xanxerê", "SC", -26.8850, -52.4150),
    ("S005", "Centro", "Concórdia", "SC", -27.2342, -52.0278),
    ("S006", "Zona sul", "Concórdia", "SC", -27.2500, -52.0300),
]
INICIO = datetime(2026, 10, 20, 0, 0, tzinfo=timezone.utc)

def popular(db, inicio=INICIO, seed=42):
    random.seed(seed)
    db.Sensores.drop(); db.Medicoes.drop()
    db.Sensores.insert_many([{
        "_id": i, "modelo": "AirMonitor-200", "descricao": f"Sensor ambiental - {d}",
        "localizacao": {"cidade": c, "uf": uf, "latitude": la, "longitude": lo},
        "ativo": True, "grandezas": GRANDEZAS} for i, d, c, uf, la, lo in SENSORES])
    docs = []
    for i, *_ in SENSORES:
        base = random.uniform(15, 30)
        for k in range(288):
            pm25 = max(1, base + random.gauss(0, 5))
            docs.append({"sensor_id": i, "timestamp": inicio + timedelta(minutes=5 * k),
                         "pm25": round(pm25, 1), "pm10": round(pm25 * random.uniform(1.8, 2.2), 1),
                         "co2": round(random.uniform(420, 650)), "temperatura": round(random.uniform(15, 30), 1),
                         "umidade": round(random.uniform(40, 90))})
    db.Medicoes.insert_many(docs)
    db.Medicoes.create_index([("sensor_id", 1), ("timestamp", -1)])
    return len(docs)

if __name__ == "__main__":
    print(f"{popular(get_db())} medições inseridas.")
