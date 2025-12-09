#!/bin/bash

# ----------------------------
# Configuration
# ----------------------------

CONTAINER_NAME="kafka-kafkabok3"     # Nom du container Docker Kafka
BOOTSTRAP="localhost:9093"         # Bootstrap server vu depuis le container
CLIENT_PROPS="/etc/kafka/secrets/client.properties"   # Chemin du fichier props DANS le container

# Arguments
USER="$1"
PASSWORD="$2"

if [ -z "$USER" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: $0 <username> <password>"
    exit 1
fi

# ----------------------------
# Create user
# ----------------------------

echo "Creating SCRAM user '$USER' with password '$PASSWORD'..."

docker exec \
  -e KAFKA_OPTS="" \
  -e KAFKA_JMX_OPTS="" \
  -e JMX_PORT="" \
  "$CONTAINER_NAME" \
  kafka-configs \
    --bootstrap-server "$BOOTSTRAP" \
    --alter \
    --add-config "SCRAM-SHA-256=[password=$PASSWORD]" \
    --entity-type users \
    --entity-name "$USER" \
    --command-config "$CLIENT_PROPS"

# ----------------------------
# Verify user creation
# ----------------------------

echo "Verifying user '$USER'..."

docker exec \
  -e KAFKA_OPTS="" \
  -e KAFKA_JMX_OPTS="" \
  -e JMX_PORT="" \
  "$CONTAINER_NAME" \
  kafka-configs \
    --bootstrap-server "$BOOTSTRAP" \
    --describe \
    --entity-type users \
    --entity-name "$USER" \
    --command-config "$CLIENT_PROPS"
