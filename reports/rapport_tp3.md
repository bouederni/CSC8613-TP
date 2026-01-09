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

## Exemple de table de snapshot

Nom : subscriptions_profile_snapshots
Quelques colonnes : 
- months_active INT,
- monthly_fee NUMERIC,
- paperless_billing BOOLEAN,
- plan_stream_tv BOOLEAN

## Utilité de `feast apply`

`feast apply` sert à synchroniser la définition du Feature Store avec les fichiers de configuration présents dans le repo. Il lit les Entities, Feature Views, Data Sources, ... puis met à jour le registry pour refléter l'état actuel du code. 

# Récupération offline & online

## Création du dataset

J'ai utilisé la commande `docker compose exec prefect python build_training_dataset.py`.
```
spipo@spipos-vbox:~/Workspace/CSC8613/TP$ head -5 data/processed/training_df.csv
user_id,event_timestamp,months_active,monthly_fee,paperless_billing,watch_hours_30d,avg_session_mins_7d,failed_payments_90d,churn_label
3957-SQXML,2024-01-31,34,24.95,False,30.9351129582808,29.141044640845102,0,False
5954-BDFSG,2024-01-31,72,107.5,True,32.7466887449717,29.141044640845102,1,True
0434-CSFON,2024-01-31,47,100.5,True,36.0906930519481,29.141044640845102,0,True
1215-FIGMP,2024-01-31,60,89.9,True,31.1684621173079,29.141044640845102,0,True
```

## Temporal correctness
Feast garantit la temporal correctness grace à deux mécanismes complémentaires : chaque DataSource définit `timestamp_field="as_of"`, ce qui indique à Feast la date à laquelle les features étaient valides, et le `entity_df` fourni pour l’extraction offline contient `user_id` et un `event_timestamp`. Lors de la jointure, Feast applique automatiquement un point-in-time join : pour chaque ligne du `entity_df`, il ne sélectionne que les features dont `as_of` est antérieur ou égal à `event_timestamp`, ce qui évite ainsi toute fuite d’information future.

## get_online_features
```
Online features for user: 9795
{'user_id': ['9795'], 'paperless_billing': [True], 'months_active': [1], 'monthly_fee': [29.85]}
```

Si l'on interroge un user_id qui n’a pas de features matérialisées, on obtiendra des valeurs à None dans les différents champs.

# Réflexion

Un endpoint /features/{user_id} basé sur Feast réduit le training‑serving skew en garantissant une source unique de vérité : mêmes définitions, schémas et transformations pour l’entraînement (offline) et l’inférence (online). 

Feast permet de recréer les features à un instant t via les snapshots (as_of) et d’exposer en production des valeurs fraîches depuis l’online store, évitant ainsi la data leakage temporelle. 

Le registry offre versioning et validation de types, ce qui assure la cohérence entre les runs d’entraînement et les appels en production. Pour être pleinement efficace, ce dispositif doit être complété par des jobs de materialize fiables, des tests de réconciliation et du monitoring des distributions de features.

Le dépôt a été tagué avec "tp3" comme demandé.