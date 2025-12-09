#!/usr/bin/env python3
import argparse
import ssl
import time

from kafka.admin import (
    KafkaAdminClient,
    NewTopic,
    ACL,
    ACLFilter,
    ResourcePattern,
    ACLPermissionType,
    ACLOperation,
    ResourceType,
)
from kafka.errors import TopicAlreadyExistsError, KafkaError

# =======================
# CONFIGURATION
# =======================
BROKERS = [
    "kafkabok1.eastus.cloudapp.azure.com:9093",
    "kafkabok2.westeurope.cloudapp.azure.com:9093",
    "kafkabok3.westeurope.cloudapp.azure.com:9093",
]

ADMIN_USERNAME = "admin"      # utilisateur admin
ADMIN_PASSWORD = "adminpass"
SASL_MECHANISM = "SCRAM-SHA-256"
SECURITY_PROTOCOL = "SASL_SSL"

# SSL contexte pour certificat auto-signé
ssl_context = ssl._create_unverified_context()


# =======================
# FONCTIONS
# =======================
def create_topic_if_not_exists(admin, topic_name, partitions=2, replication=3):
    """Crée un topic s'il n'existe pas déjà."""
    try:
        topic = NewTopic(
            name=topic_name,
            num_partitions=partitions,
            replication_factor=replication,
        )
        admin.create_topics([topic])
        print(f"✅ Topic '{topic_name}' créé.")
    except TopicAlreadyExistsError:
        print(f"ℹ️ Topic '{topic_name}' existe déjà.")
    except KafkaError as e:
        print(f"❌ Erreur lors de la création du topic : {e}")


def create_user_acl(admin, user, topic_name):
    """Crée des ACL READ/WRITE pour un user sur un topic et les affiche."""
    try:
        resource = ResourcePattern(ResourceType.TOPIC, topic_name)

        acl_read = ACL(
            principal=f"User:{user}",
            host="*",
            operation=ACLOperation.READ,
            permission_type=ACLPermissionType.ALLOW,
            resource_pattern=resource,
        )

        acl_write = ACL(
            principal=f"User:{user}",
            host="*",
            operation=ACLOperation.WRITE,
            permission_type=ACLPermissionType.ALLOW,
            resource_pattern=resource,
        )

        result = admin.create_acls([acl_read, acl_write])
        print(f"✅ ACL read/write pour '{user}' sur le topic '{topic_name}' créées.")
        print(f"   Détail résultat create_acls: {result}")

        time.sleep(5)

        acl_filter = ACLFilter(
            principal=f"User:{user}",
            host="*",
            operation=ACLOperation.ANY,
            permission_type=ACLPermissionType.ANY,
            resource_pattern=resource,
        )

        acls, error = admin.describe_acls(acl_filter)

        print(f"\n🔎 ACLs sur le topic '{topic_name}' pour l'utilisateur '{user}':")
        if error is not None and error.__name__ != "NoError":
            print(f"⚠️ Erreur renvoyée par describe_acls : {error}")
        if not acls:
            print("   (Aucune ACL trouvée)")
        else:
            for acl in acls:
                print(
                    f" - ResourceType: {acl.resource_pattern.resource_type.name}, "
                    f"ResourceName: {acl.resource_pattern.resource_name}, "
                    f"PatternType: {acl.resource_pattern.pattern_type.name}, "
                    f"Principal: {acl.principal}, "
                    f"Opération: {acl.operation.name}, "
                    f"Permission: {acl.permission_type.name}, "
                    f"Host: {acl.host}"
                )

    except KafkaError as e:
        print(f"❌ Erreur lors de la création ou vérification des ACL : {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Créer topic + user ACL read/write sur Kafka SASL_SSL."
    )

    parser.add_argument(
        "--user",
        "-u",
        type=str,
        required=True,
        help="Nom du user Kafka (principal ACL, ex: client1)",
    )
    parser.add_argument(
        "--topic",
        "-t",
        type=str,
        required=True,
        help="Nom du topic Kafka (ex: testn1)",
    )
    parser.add_argument(
        "--partitions",
        type=int,
        default=2,
        help="Nombre de partitions du topic (défaut: 2)",
    )
    parser.add_argument(
        "--replication",
        type=int,
        default=3,
        help="Facteur de réplication du topic (défaut: 3)",
    )

    args = parser.parse_args()

    admin = None
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=BROKERS,
            security_protocol=SECURITY_PROTOCOL,
            sasl_mechanism=SASL_MECHANISM,
            sasl_plain_username=ADMIN_USERNAME,
            sasl_plain_password=ADMIN_PASSWORD,
            ssl_context=ssl_context,
            client_id="python-admin",
        )

        create_topic_if_not_exists(
            admin, args.topic, args.partitions, args.replication
        )
        create_user_acl(admin, args.user, args.topic)

    except KafkaError as e:
        print(f"❌ Erreur de connexion au broker : {e}")
    finally:
        if admin is not None:
            try:
                admin.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()

