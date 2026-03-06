# 🏥 Projet IoT Hospitalier : Système de Détection d'Intrusions (IDS)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red)](https://www.raspberrypi.com/)

## 📋 Table des matières
- [Présentation du projet](#-présentation-du-projet)
- [Origine des données](#-origine-des-données)
- [Architecture du système](#-architecture-du-système)
- [Modèles implémentés](#-modèles-implémentés)
- [Résultats obtenus](#-résultats-obtenus)
- [Dashboard interactif](#-dashboard-interactif)
- [Déploiement sur Raspberry Pi](#-déploiement-sur-raspberry-pi)
- [Installation et utilisation](#-installation-et-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Auteurs](#-auteurs)

---

## 🎯 Présentation du projet

### Contexte
Dans les environnements hospitaliers modernes, de plus en plus de dispositifs médicaux sont connectés à Internet (IoMT - Internet of Medical Things) : moniteurs cardiaques, pompes à insuline, respirateurs, etc. Cette connectivité améliore les soins mais expose également les patients à des risques de cybersécurité majeurs. Une attaque réussie pourrait avoir des conséquences vitales.

### Problématique
Comment détecter efficacement les intrusions dans le trafic réseau d'un hôpital **tout en respectant les contraintes** des dispositifs Edge (faible consommation énergétique, ressources limitées) ?

### Objectifs
Notre projet vise à :
- ✅ **Détecter** les anomalies réseau avec une haute précision
- ✅ **Optimiser** la consommation énergétique pour un fonctionnement sur batterie
- ✅ **Visualiser** les alertes en temps réel via un dashboard
- ✅ **Déployer** l'ensemble sur une Raspberry Pi (architecture Edge)

---

## 📊 Origine des données

### Pourquoi ce dataset ?
Nous avons choisi le dataset **CICIoT2023** du Canadian Institute for Cybersecurity pour plusieurs raisons :
- **Spécificité IoT** : Contrairement aux datasets réseau classiques, celui-ci est spécifiquement conçu pour l'Internet des Objets
- **Actualité** : Publié en 2023, il reflète les menaces récentes
- **Diversité** : Il contient plusieurs types d'attaques réalistes
- **Volume** : Assez grand pour entraîner des modèles robustes

### Caractéristiques
Notre dataset fusionné contient :
- **200 000 échantillons** après fusion
- **39 caractéristiques** réseau par échantillon (durée, flags TCP, tailles de paquets, etc.)
- **4 types de trafic** :
  - `Benign` : Trafic normal (25%)
  - `DDoS-TCP Flood` : Attaques par inondation TCP (25%)
  - `DNS Spoofing` : Usurpation DNS (25%)
  - `Recon-PortScan` : Scan de ports (25%)

> **Note** : Le dataset original est trop volumineux pour GitHub. Il est disponible sur le [site officiel du CIC](https://www.unb.ca/cic/datasets/iotdataset-2023.html).

---

## 🏗️ Architecture du système

Nous avons conçu notre système selon un **modèle en 4 couches**, standard dans l'industrie IoT :

### 1. Couche de perception (Sensing Layer)
- **Rôle** : Acquérir les données réseau
- **Notre implémentation** : Chargement et fusion des fichiers CSV du dataset CICIoT2023
- **Pourquoi** : Pour simuler un flux réseau réaliste

### 2. Couche réseau (Network Layer)
- **Rôle** : Transmettre les données du capteur au serveur
- **Notre approche** : Nous avons simulé et comparé 3 stratégies de transmission :

| Stratégie | Description | Avantage | Inconvénient | Paquets transmis/1000 | Énergie |
|-----------|-------------|----------|--------------|----------------------|---------|
| **S1 - Immédiate** | Transmission de chaque paquet | Faible latence | Consommation élevée | 1000 | 100.0 |
| **S2 - Agrégée** | Regroupement par lots de 10 | Économie d'énergie | Latence accrue | 100 | 5.0 |
| **S3 - Conditionnelle** | Transmission uniquement si anomalie | Très économe | Dépend du modèle | 218 | 17.44 |

**Pourquoi ces stratégies ?**  
Dans un environnement hospitalier, le compromis énergie/latence est crucial. La stratégie conditionnelle (S3) offre le meilleur équilibre, réduisant de **78%** le nombre de transmissions.

### 3. Couche de traitement (Data Processing Layer)
- **Rôle** : Analyser les données et détecter les anomalies
- **Notre implémentation** : 7 modèles TinyML comparés et optimisés
- **Pourquoi TinyML** : Pour fonctionner sur des dispositifs à ressources limitées (Raspberry Pi)

### 4. Couche application (Application Layer)
- **Rôle** : Visualiser les résultats et alerter
- **Notre implémentation** : Dashboard Streamlit avec 3 pages
- **Pourquoi Streamlit** : Rapidité de développement, interactivité, déploiement facile

---

## 🤖 Modèles implémentés

### Pourquoi 7 modèles ?
Nous avons choisi de comparer plusieurs approches pour identifier le meilleur compromis **performance / consommation énergétique** :

1. **Seuil simple** : Baseline ultra-légère
2. **Régression logistique** : Modèle linéaire interprétable
3. **Arbre de décision** : Non-linéaire mais interprétable
4. **Arbre optimisé** : Version améliorée par Grid Search
5. **Régression pondérée** : Pour gérer le déséquilibre des classes
6. **Random Forest** : Approche ensemble plus robuste
7. **Voting Classifier** : Combinaison des meilleurs modèles

### Améliorations réalisées

#### 🔧 Amélioration 1 : Grid Search
Nous avons optimisé l'arbre de décision en testant systématiquement 240 combinaisons d'hyperparamètres :
- Profondeur : 3, 5, 7, 10, 15
- Échantillons min pour division : 2, 5, 10, 20
- Échantillons min par feuille : 1, 2, 5, 10
- Features max : 'sqrt', 'log2', None

**Résultat** : Accuracy passée de **85.50% → 88.17%** (+2.67%)

#### ⚖️ Amélioration 2 : Régression pondérée
Face au déséquilibre des classes (25% normal, 75% attaque), nous avons appliqué des poids :
- Classe normale : 2.0
- Classe attaque : 0.667

**Pourquoi** : Pénaliser plus lourdement les erreurs sur la classe minoritaire

#### 🌲 Amélioration 3 : Random Forest léger
50 arbres de profondeur 5 pour un compromis robustesse/légèreté

#### 🔬 Amélioration 4 : Feature Engineering
Création de 4 nouvelles caractéristiques :
- Ratio SYN/ACK
- Taille moyenne des paquets
- Débit réseau
- Interaction FIN/RST

#### 🗳️ Amélioration 5 : Voting Classifier
Combinaison pondérée des 3 meilleurs modèles :
- Arbre optimisé (poids 2)
- Régression pondérée (poids 1)
- Random Forest (poids 2)

---

## 📈 Résultats obtenus

### Tableau comparatif des 7 modèles

| Modèle | Accuracy | Précision (attaque) | Rappel (attaque) | F1-score | Énergie (J/100 inf.) |
|--------|----------|---------------------|-------------------|----------|----------------------|
| Seuil simple | 77.27% | 0.83 | 0.88 | 0.85 | 0.7246 |
| Régression logistique | 81.68% | 0.85 | 0.92 | 0.88 | 0.0407 |
| Arbre de décision (base) | 85.50% | 0.87 | 0.95 | 0.91 | 0.0790 |
| **Arbre optimisé** | **88.17%** | **0.89** | **0.96** | **0.92** | **0.0790** |
| Régression pondérée | 76.22% | 0.93 | 0.74 | 0.82 | 0.0407 |
| Random Forest léger | 83.32% | 0.88 | 0.93 | 0.90 | 0.0790 |
| Voting Classifier | 88.08% | 0.88 | 0.95 | 0.91 | 0.0790 |

### 🏆 Modèle retenu
Nous avons sélectionné l'**arbre de décision optimisé** pour les raisons suivantes :
- **Meilleure accuracy** : 88.17%
- **Excellent rappel** : 96% des attaques détectées
- **Interprétable** : Les règles de décision sont compréhensibles (important en milieu médical)
- **Léger** : Inférence rapide, mémoire faible

---

## 📊 Dashboard interactif

### Pourquoi un dashboard ?
Pour permettre une **supervision en temps réel** et rendre les résultats accessibles au personnel hospitalier (non-technique).

### Technologies utilisées
- **Streamlit** : Framework principal
- **Plotly** : Graphiques interactifs
- **Pandas** : Manipulation des données
- **JSON** : Communication temps réel

### Structure du dashboard

#### 🏠 Page Accueil
- Indicateurs clés (KPI) : total échantillons, trafic normal, attaques, taux
- Graphiques de répartition du trafic
- Statistiques mises à jour en temps réel

#### ⚙️ Page Modèles
- Tableau comparatif des 7 modèles
- Graphiques d'accuracy et consommation énergétique
- Mise en évidence du meilleur modèle

#### 🚨 Page Alertes
- Historique des dernières détections
- Code couleur (🔴 attaque, 🟢 normal)
- Rafraîchissement automatique

### Communication temps réel
Le dashboard communique avec le simulateur via un **fichier JSON partagé** :
1. Le simulateur écrit les détections toutes les 2 secondes
2. Le dashboard lit et met à jour l'affichage
3. Les statistiques se recalculent automatiquement

---

## 🖥️ Déploiement sur Raspberry Pi

### Pourquoi la Raspberry Pi ?
- **Représentative** d'un dispositif Edge réel
- **Accessible** et peu coûteuse
- **Documentation** abondante

### Étapes de déploiement

#### 1. Préparation de la carte SD
- Utilisation de **Raspberry Pi Imager**
- Installation de **Raspberry Pi OS (32-bit)**
- Activation SSH et configuration WiFi (`TP-Link_4F1A`)

#### 2. Problème rencontré et résolution
**Symptôme** : LED verte clignotant 7-8 fois → corruption du noyau
**Solution** : Reformatage avec **SD Card Formatter** et réécriture de l'image

#### 3. Transfert des fichiers
```bash
scp *.pkl *.py pi@192.168.11.134:~/
```
Pourquoi ces fichiers ?
*.pkl : Les modèles entraînés et le scaler
*.py : Les scripts Python (dashboard, simulateur, mock)

#### 4. Configuration Python
# Création environnement virtuel
  python3 -m venv streamlit_env
  source streamlit_env/bin/activate
# Installation des dépendances
  pip install -r requirements.txt
**Pourquoi un environnement virtuel ?**
  Pour isoler les dépendances du projet et éviter les conflits avec les paquets système de la Raspberry Pi.

#### 5. Adaptation pour ARM
**Problème rencontré** : La bibliothèque pyarrow (utilisée par Streamlit) ne se compile pas correctement sur architecture ARM (Raspberry Pi).
**Solution mise en œuvre** :
   -Création d'un mock PyArrow (streamlit_no_pyarrow.py) qui simule la présence de la bibliothèque
   -Remplacement des composants Streamlit problématiques par des alternatives HTML natives
   -Utilisation de l'option --no-deps pour éviter l'installation automatique des dépendances problématiques
**Pourquoi cette adaptation ?**
Pour garantir le fonctionnement du dashboard sur la Raspberry Pi sans nécessiter de compilation native complexe.

#### 6. Lancement
```bash
# Terminal 1 - Lancer le dashboard
cd ~
source streamlit_env/bin/activate
python -m streamlit run dashboard_iot_pi_final_v3.py --server.port 8501

# Terminal 2 - Lancer le simulateur (dans une autre session SSH)
ssh pi@[IP_RASPBERRY]
source streamlit_env/bin/activate
cd ~
python test_detections.py
```
**Accès au dashboard** : http://[IP_RASPBERRY]:8501
**Pourquoi deux terminaux ?**
Le dashboard et le simulateur sont deux processus indépendants qui communiquent via un fichier JSON partagé.

#### 🚀 Installation et utilisation
**Prérequis**
  Python 3.9 ou supérieur
  Git
  (Optionnel) Raspberry Pi 5 pour déploiement réel
  (Optionnel) Câble Ethernet pour connexion directe

**Installation locale (sur PC)**
bash
# 1. Cloner le dépôt
  git clone https://github.com/bougsfati/iot-hospital-ids.git
  cd iot-hospital-ids
# 2. Créer l'environnement virtuel
  python -m venv venv
# 3. Activer l'environnement
# Sur Windows :
  venv\Scripts\activate
# Sur Linux/Mac :
  source venv/bin/activate
# 4. Installer les dépendances
  pip install -r requirements.txt
# 5. Lancer le dashboard
  cd dashboard
  streamlit run dashboard_iot_pi_final_v3.py
  Utilisation
  Ouvrir le dashboard : http://localhost:8501

**Explorer les pages** :

🏠 Accueil : Visualisation des statistiques globales
⚙️ Modèles : Comparaison des 7 modèles
🚨 Alertes : Détections en temps réel

*Lancer la simulation (dans un autre terminal)** :
bash
cd dashboard
python test_detections.py

#### 📁 Structure du projet
iot-hospital-ids/
│
├── 📁 data/                         # Données
│   ├── 📁 raw/                       # Données brutes (CICIoT2023)
│   │   └── README.md                  # Instructions pour télécharger
│   └── 📁 processed/                  # Données préparées
│       └── dataset_iot_prepare.csv    # Dataset fusionné (200k lignes)
│
├── 📁 notebooks/                     # Notebooks Jupyter
│   ├── 1_exploration_donnees.ipynb
│   ├── 2_modeles_base.ipynb
│   ├── 3_ameliorations_modeles.ipynb
│   └── 4_evaluation_finale.ipynb
│
├── 📁 src/                           # Code source
│   ├── __init__.py
│   ├── preprocessing.py               # Fonctions de prétraitement
│   ├── models.py                      # Définition des modèles
│   └── utils.py                       # Fonctions utilitaires
│
├── 📁 models/                         # Modèles entraînés
│   ├── modele_logistic_regression.pkl
│   ├── scaler.pkl
│   ├── modele_arbre_optimise.pkl
│   └── modele_raspberry_final.pkl
│
├── 📁 dashboard/                      # Application Streamlit
│   ├── dashboard_iot_pi_final_v3.py   # Dashboard principal
│   ├── test_detections.py              # Simulateur d'alertes
│   ├── streamlit_no_pyarrow.py         # Mock PyArrow
│   └── detection_realtime.json         # Fichier de communication
│
├── 📁 scripts/                        # Scripts utilitaires
│   ├── train_all_models.py             # Entraînement de tous les modèles
│   └── deploy_to_raspberry.sh          # Script de déploiement
│
├── 📁 docs/                           # Documentation
│   ├── architecture_4_couches.md
│   ├── strategies_transmission.md
│   └── deployment_guide.md
│
├── 📁 results/                        # Résultats et figures
│   ├── 📁 figures/
│   │   ├── matrice_confusion.png
│   │   ├── comparaison_modeles.png
│   │   └── dashboard_screenshot.png
│   └── tableau_resultats.csv
│
├── .gitignore                         # Fichiers ignorés par Git
├── README.md                          # Ce fichier
├── LICENSE                            # Licence MIT
├── requirements.txt                   # Dépendances Python
└── environment.yml                    # Dépendances Conda (optionnel)


#### 👥 Auteurs
-Fatima Ezzahra Bougsissa
-Sara Bouras
-Maryem Trifis
-Hamza Harakat
-Nada Mahrouz
