import argparse
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable
import socket
import time
import ssl

# =======================
# CONFIGURATION
# =======================
BROKERS = [
    "kafkabok1.eastus.cloudapp.azure.com:9093",
    "kafkabok2.westeurope.cloudapp.azure.com:9093",
    "kafkabok3.westeurope.cloudapp.azure.com:9093"
]

SASL_USERNAME = "admin"
SASL_PASSWORD = "adminpass"
SASL_MECHANISM = "SCRAM-SHA-256"
SECURITY_PROTOCOL = "SASL_SSL"

# =======================
# FONCTIONS
# =======================

def check_brokers(brokers, timeout=5):
    """Vérifie quels brokers sont accessibles"""
    accessible = []
    inaccessible = []
    for broker in brokers:
        host, port = broker.split(":")
        try:
            print(f"🔍 Test du broker {broker}...")
            sock = socket.create_connection((host, int(port)), timeout=timeout)
            sock.close()
            accessible.append(broker)
        except Exception:
            inaccessible.append(broker)
    return accessible, inaccessible


def create_topic(topic_name, partitions=2, replication=3):
    accessible, inaccessible = check_brokers(BROKERS)

    if inaccessible:
        print(f"❌ Brokers inaccessibles : {inaccessible}")
    if not accessible:
        print("❌ Aucun broker accessible. Abandon de la création du topic.")
        return

    try:
        # Création d'un contexte SSL qui ignore les certificats auto-signés
        ssl_context = ssl._create_unverified_context()

        admin = KafkaAdminClient(
            bootstrap_servers=accessible,
            security_protocol=SECURITY_PROTOCOL,
            sasl_mechanism=SASL_MECHANISM,
            sasl_plain_username=SASL_USERNAME,
            sasl_plain_password=SASL_PASSWORD,
            ssl_context=ssl_context,
            client_id='python-admin'
        )

        topic = NewTopic(
            name=topic_name,
            num_partitions=partitions,
            replication_factor=replication
        )

        admin.create_topics([topic], timeout_ms=15000)
        print(f"✅ Topic '{topic_name}' créé avec succès !")

        # Vérification avec retry
        max_wait = 10  # secondes
        interval = 1
        elapsed = 0
        found = False
        while elapsed < max_wait:
            topics = admin.list_topics()
            if topic_name in topics:
                found = True
                break
            time.sleep(interval)
            elapsed += interval

        if found:
            print(f"🔎 Vérification OK : le topic '{topic_name}' existe bien dans la liste.")
        else:
            print(f"❌ Vérification FAILED : le topic '{topic_name}' n'apparaît pas après {max_wait} secondes.")

    except NoBrokersAvailable:
        print("❌ Aucun broker Kafka disponible pour créer le topic.")
    except Exception as e:
        print(f"❌ Erreur lors de la création du topic : {e}")
    finally:
        try:
            admin.close()
        except:
            pass


# =======================
# MAIN
# =======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Créer un topic Kafka SASL_SSL (certificat auto-signé).")

    parser.add_argument("topic", type=str, help="Nom du topic à créer")
    parser.add_argument("--partitions", type=int, default=2, help="Nombre de partitions")
    parser.add_argument("--replication", type=int, default=3, help="Facteur de réplication")

    args = parser.parse_args()

    create_topic(args.topic, args.partitions, args.replication)

