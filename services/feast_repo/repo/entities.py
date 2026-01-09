from feast import Entity
from feast.types import ValueType

# Définition de l'entité principale "user"
user = Entity(
    name="user",
    join_keys=["user_id"],
    description="Représente un utilisateur unique identifié par user_id",
    value_type=ValueType.STRING,
)