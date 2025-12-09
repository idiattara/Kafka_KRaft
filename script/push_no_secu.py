import argparse
from kafka import KafkaProducer

# ============================
# Arguments CLI
# ============================
parser = argparse.ArgumentParser(description="Kafka producer simple en PLAINTEXT")
parser.add_argument("--topic", type=str, required=True, help="Nom du topic Kafka")
args = parser.parse_args()

TOPIC = args.topic

# ============================
# Configuration Kafka
# ============================
BROKER = [
    "kafkabok1.eastus.cloudapp.azure.com:9093",
    "kafkabok2.westeurope.cloudapp.azure.com:9093",
    "kafkabok3.westeurope.cloudapp.azure.com:9093"
]

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    security_protocol="PLAINTEXT",
    value_serializer=lambda v: v.encode("utf-8"),
    acks='all'
)

# ============================
# Envoi du message
# ============================
message = f"Bonjour depuis Python en PLAINTEXT 👋 (topic={TOPIC})"
future = producer.send(TOPIC, value=message)

try:
    record_metadata = future.get(timeout=10)
    print(
        f"✅ Message confirmé sur '{record_metadata.topic}', "
        f"partition {record_metadata.partition}, offset {record_metadata.offset}"
    )
except Exception as e:
    print(f"❌ Erreur lors de l'envoi : {e}")

producer.flush()
producer.close()

