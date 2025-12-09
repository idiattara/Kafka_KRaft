# Confluent Platform 8.0.1 — Kafka (KRaft 3 nœuds) + Kafka Connect
Déploiement via **Ansible + Docker Compose** (sans Java sur l’hôte).

## Inventaire
Voir `inventories/production/hosts.ini` (3 brokers/controllers + 1 Connect).

## Variables
- `group_vars/kafka_brokers.yml` : ports, RF, chemins data/logs, **kafka_cluster_id**, etc.
- `group_vars/kafka_connect.yml` : ports, topics internes RF, bootstrap auto depuis l’inventaire.

## JMX (Kafka uniquement)
Placez **obligatoirement** dans `roles/kafka/files/` :
- `jmx_prometheus_javaagent.jar`
- `kafka_jmx.yml`

## Cluster ID (KRaft)
Générez un ID unique et identique pour tout le cluster :
```bash
docker run --rm confluentinc/cp-kafka:8.0.1 kafka-storage random-uuid
```
Mettez-le dans `kafka_cluster_id` (group_vars).

## Exécution
```bash
ansible-galaxy collection install -r collections/requirements.yml
ansible-playbook -i inventories/production/hosts.ini site.yml
```

## Notes
- Le rôle **kafka** formate le storage KRaft **une seule fois** par nœud s’il ne voit pas `meta.properties`.
- **Connect** : configuration `connect-distributed.properties` montée dans le conteneur ; ajoutez vos connecteurs/plug-ins sous `/opt/connectors` si besoin (à monter côté host).
