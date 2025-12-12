# producer_ventes.py
"""
Kafka Producer: Sales Data Simulator
Sends one sales record every 2 seconds to 'ventes_stream' topic.
"""

import json
import time
import random
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime

# Configuration
KAFKA_TOPIC = "ventes_stream"
KAFKA_SERVER = "localhost:9092"
BATCH_INTERVAL = 2  # seconds

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Données de base
PRODUITS = [
    {"id": 101, "nom": "Ordinateur portable", "categorie": "Électronique", "prix": 899.99},
    {"id": 102, "nom": "Souris sans fil", "categorie": "Électronique", "prix": 25.50},
    {"id": 103, "nom": "Clavier mécanique", "categorie": "Électronique", "prix": 75.00},
    {"id": 104, "nom": "Casque audio", "categorie": "Électronique", "prix": 59.99},
    {"id": 105, "nom": "Livre 'Data Science'", "categorie": "Livre", "prix": 19.99},
    {"id": 106, "nom": "Écran 27 pouces", "categorie": "Électronique", "prix": 299.99},
]

CLIENTS = [
    {"id": 1, "nom": "Jean Dupont", "ville": "Paris", "pays": "France", "segment": "Particulier"},
    {"id": 2, "nom": "Maria Garcia", "ville": "Madrid", "pays": "Espagne", "segment": "Particulier"},
    {"id": 3, "nom": "John Smith", "ville": "Londres", "pays": "UK", "segment": "Entreprise"},
    {"id": 4, "nom": "Sophie Martin", "ville": "Lyon", "pays": "France", "segment": "Particulier"},
    {"id": 5, "nom": "Klaus Mueller", "ville": "Berlin", "pays": "Allemagne", "segment": "Entreprise"},
]


def delivery_report(err, msg):
    """Callback for delivery reports"""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def create_producer():
    """Initialize Kafka Producer with error handling"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1
        )
        logger.info(f"✅ Connected to Kafka broker: {KAFKA_SERVER}")
        return producer
    except KafkaError as e:
        logger.error(f"❌ Failed to connect to Kafka: {e}")
        raise


def generate_sales():
    """Generate random sales records"""
    vente_id = 1
    
    try:
        producer = create_producer()
        logger.info("🚀 Sales Producer started. Sending records every 2 seconds...")
        
        while True:
            # Générer une vente aléatoire
            client = random.choice(CLIENTS)
            produit = random.choice(PRODUITS)
            quantite = random.randint(1, 5)
            montant = round(quantite * produit["prix"], 2)

            vente = {
                "vente_id": vente_id,
                "client_id": client["id"],
                "produit_id": produit["id"],
                "timestamp": datetime.now().isoformat(),
                "quantite": quantite,
                "montant": montant,
                "client_nom": client["nom"],
                "produit_nom": produit["nom"],
                "categorie": produit["categorie"],
                "pays": client["pays"],
                "segment": client["segment"]
            }

            # Envoyer au topic Kafka (async avec callback)
            future = producer.send(KAFKA_TOPIC, value=vente)
            future.add_callback(delivery_report).add_errback(delivery_report)
            
            logger.info(f"📤 Sale #{vente_id}: {vente['client_nom']} - {vente['produit_nom']} - €{vente['montant']}")

            vente_id += 1
            time.sleep(BATCH_INTERVAL)

    except KeyboardInterrupt:
        logger.info("🛑 Producer stopped by user.")
    except Exception as e:
        logger.error(f"❌ Producer error: {e}")
    finally:
        if producer:
            producer.flush()
            producer.close()
            logger.info("Producer connection closed.")


if __name__ == "__main__":
    generate_sales()