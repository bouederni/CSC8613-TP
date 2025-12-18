# Contexte
On dispose d'un ensemble de données structurées comprenant des snapshots mensuels sur deux périodes, ainsi que des tables opérationnelles décrivant des utilisateurs, leur usage, abonnements, paiements et interactions avec le support.
L'objectif du TP 3 est de connecter ces données au Feature Store Feast, afin de définir & matérialiser des features, puis de les récupérer à la fois en mode offline (pour l'entraînement ou l'analyse) et en mode online (pour l'inférence temps réel). Enfin, on va mettre en place un endpoint API simple capable de charger ces features online pour servir un modèle ou un score à la demande.
# Mise en place de Feast
Pour démarrer les services, j'ai utilisé `docker compose up -d --build`.
Le conteneur tp-feast-1 contient toute la configuration du Feature Store : 
- Le fichier `feature_store.yaml`
- Les définitions des features
- Les sources des données

On l'utilise comme point d'accès central pour gérer le store, en exécutant les commandes via `docker compose exec feast ...`, par exemple pour appliquer la configuration (`feast apply`) ou matérialiser les features dans la couche online (`feast materialize`).

Dans Feast, une `Entity` représente l'objet principal autour duquel les features sont organisées. Elle définit l'identifiant commun permettant de relier les différentes sources de données et de retrouver les features pertinentes pour une même instance.

Dans StreamFlow, `user_id` est un bon choix de clé de jointure car il identifie de manière unique chaque utilisateur à travers toutes les tables (usages, abonnements, paiements, support...). 

# Définition du Feature Store

# Récupération offline & online

# Réflexion
    