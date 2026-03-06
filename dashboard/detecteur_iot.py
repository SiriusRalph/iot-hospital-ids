import json
import time
import random
from datetime import datetime

def envoyer_vers_streamlit(resultat):
    """Envoie les détections vers le dashboard Streamlit via un fichier JSON."""
    try:
        # Pour Linux/Mac : /tmp/detection_realtime.json
        # Pour Windows : "C:/temp/detection_realtime.json" (crée le dossier C:/temp si besoin)
        chemin = "detection_realtime.json"  # adapte pour Windows
        with open(chemin, 'w') as f:
            json.dump(resultat, f)
    except Exception as e:
        print(f"Erreur d'écriture : {e}")

if __name__ == "__main__":
    print("Simulateur de détections en cours...")
    while True:
        detection = {
            'timestamp': datetime.now().isoformat(),
            'est_attaque': random.choice([True, False]),
            'confiance': random.randint(70, 99),
            'type': 'attaque' if random.choice([True, False]) else 'normal'
        }
        envoyer_vers_streamlit(detection)
        time.sleep(2)