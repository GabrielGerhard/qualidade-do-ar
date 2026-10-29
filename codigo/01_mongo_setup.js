// mongosh: load("codigo/01_mongo_setup.js")
use("QualidadeAr");
db.Medicoes.createIndex({ sensor_id: 1, timestamp: -1 });
