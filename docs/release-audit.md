# Audit de publication — V1 publique

Cette note résume les contrôles exécutés avant création de l'archive publique.

## Contrôles réalisés

- `pytest` : **5 tests passés**.
- Compilation Python (`compileall`) : **OK**.
- Contrôle de publication (`scripts/public_release_check.py`) : **OK**.
- Parsing YAML de `docker-compose.yml` et `.github/dependabot.yml` : **OK**.
- Scan AST : **0** `eval`/`exec`, **0** sous-processus sans timeout, **0** appel HTTP `requests` sans timeout, **0** `except:` nu.
- Démonstration synthétique : **3 CV fictifs**, **3 filières fictives**, **9 résultats de matching**.
- Persistance de démonstration : **3 documents** et **9 résultats** enregistrés dans SQLite.
- Scan de marqueurs privés : aucun JWT/Bearer embarqué, aucun chemin utilisateur de production, aucun endpoint privé connu de la V1, aucun nom de CV réel utilisé comme donnée d'exemple.
- Construction locale du package sans dépendances et sans isolation réseau : **OK**.
- Simulation `git add .` : seuls les fichiers du kit public sont suivis.

## Limite de validation

Le moteur Docker n'était pas disponible dans l'environnement de préparation. Les Dockerfiles et le fichier Compose ont donc été revus statiquement, mais aucun `docker compose build` / `docker compose up` end-to-end n'est revendiqué dans cet audit.

Les connecteurs distants sont fournis comme exemples configurables et n'ont pas été exécutés contre les systèmes métier d'origine.
