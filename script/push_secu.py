import argparse
import ssl
from kafka import KafkaProducer


def main():
    # ============================
    # Arguments CLI
    # ============================
    parser = argparse.ArgumentParser(description="Producer Kafka SASL_SSL")

    parser.add_argument("--broker", type=str,
                        default="kafkabok3.westeurope.cloudapp.azure.com:9093",
                        help="Adresse du broker Kafka")

    parser.add_argument("--topic", type=str, required=True,
                        help="Nom du topic Kafka")

    parser.add_argument("--user", type=str, required=True,
                        help="Nom du user Kafka (SASL)")

    args = parser.parse_args()

    BROKER = args.broker
    TOPIC = args.topic
    USERNAME = args.user

    # Mot de passe FIXE
    PASSWORD = "password"

    # ============================
    # SSL Context
    # ============================
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # ============================
    # Kafka Producer
    # ============================
    producer = KafkaProducer(
        bootstrap_servers=[BROKER],
        security_protocol="SASL_SSL",
        ssl_context=context,
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=USERNAME,
        sasl_plain_password=PASSWORD,  # <--- PASSWORD FIXE
        value_serializer=lambda v: v.encode("utf-8"),
        acks='all'
    )

    message = f"Bonjour depuis Python 👋 (topic={TOPIC}, user={USERNAME})"

    future = producer.send(TOPIC, value=message)

    try:
        record_metadata = future.get(timeout=10)
        print(f"✅ Message confirmé sur le topic '{record_metadata.topic}', "
              f"partition {record_metadata.partition}, offset {record_metadata.offset}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message : {e}")

    producer.flush()


if __name__ == "__main__":
    main()

