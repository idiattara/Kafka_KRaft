#!/bin/bash

# Configuration
COMMON_NAME="kafkabok3.westeurope.cloudapp.azure.com"
VALIDITY_DAYS=365
STOREPASS="changeit"

echo "1. Génération de la clé privée root..."
openssl genrsa -out root.key 2048

echo "2. Génération du certificat auto-signé root..."
openssl req -new -x509 -key root.key -out root.crt -days $VALIDITY_DAYS \
-subj "/C=FR/ST=France/L=Clermont-Ferrand/O=MyCompany/OU=IT/CN=MyKafkaCA"

echo "3. Création du truststore Kafka avec le certificat root..."
keytool -import -keystore kafka.truststore.jks -alias CARoot -file root.crt \
  -storepass $STOREPASS -noprompt

echo "4. Génération du keystore Kafka01 et de la clé privée avec SAN..."
keytool -genkey -keystore kafka01.keystore.jks \
  -alias localhost \
  -validity $VALIDITY_DAYS \
  -keyalg RSA \
  -storepass $STOREPASS \
  -dname "CN=$COMMON_NAME, OU=IT, O=MyCompany, L=Clermont-Ferrand, ST=France, C=FR" \
  -ext SAN=DNS:$COMMON_NAME

echo "5. Création d'une CSR (demande de certificat)..."
keytool -certreq -keystore kafka01.keystore.jks \
  -alias localhost \
  -file kafka01.unsigned.crt \
  -storepass $STOREPASS

echo "6. Signature du certificat avec la CA (root)..."
openssl x509 -req -CA root.crt -CAkey root.key \
  -in kafka01.unsigned.crt \
  -out kafka01.signed.crt \
  -days $VALIDITY_DAYS \
  -CAcreateserial

echo "7. Import du certificat root dans le keystore Kafka01..."
keytool -import -keystore kafka01.keystore.jks \
  -alias CARoot \
  -file root.crt \
  -storepass $STOREPASS \
  -noprompt

echo "8. Import du certificat signé dans le keystore Kafka01..."
keytool -import -keystore kafka01.keystore.jks \
  -alias localhost \
  -file kafka01.signed.crt \
  -storepass $STOREPASS

echo "✅ Terminé ! Certificats et keystores/truststores générés avec succès."
