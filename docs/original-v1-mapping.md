# Mapping de la V1 historique vers le dépôt public

Le POC fourni pour analyse utilisait des noms de scripts liés aux différentes itérations de développement. Pour le dépôt public, ils ont été regroupés par responsabilité.

| Script / responsabilité V1 | Module public | Rôle conservé |
|---|---|---|
| `00-run-update-CV-form-stag_MySQL_V3.py` | `cli.py` / orchestration de démonstration | Enchaînement des traitements |
| `01-Quest_fil-mod_MySQL_V3.py` | `reference.py` | Construction du référentiel filières/modules, nettoyage, tags, poids |
| `02-OCR-preprocess-MySQL_VZ2.py` | `document_processing.py` | Conversion documentaire, extraction texte et OCR local |
| `03-CV_TAG_process_MySQL_V3.py` | `normalization.py` + `pipeline.py` | Normalisation, tokenisation, fréquence et tags canoniques |
| `04-Matching_and_input_process_V4.py` | `scoring.py` + `pipeline.py` | Matrice de présence, matching booléen et pondéré |
| `06-product-results-...py` | `matching_results.csv` | Restitution par filière et mots-clés |
| scripts Beetween / Quest / NoCRM | `sources/consolidation.py` | Normalisation de sources métier hétérogènes |
| script OneDrive / SharePoint | frontière documentée, non connectée par défaut | Centralisation des fichiers et exports |

## Remarque sur les noms `MySQL`

Les noms de plusieurs scripts historiques contenaient `MySQL`, mais le code V1 fourni pour cette publication utilisait effectivement **SQLite via SQLAlchemy** pour les bases locales du pipeline. Le dépôt public utilise donc des noms neutres et décrit le stockage sans reprendre cette convention historique.

## Ce qui n'est pas publié

- la V2 ultérieure ;
- les bases réelles et dictionnaires métier complets ;
- les endpoints et identifiants des services d'origine ;
- les scripts archivés/de test ;
- les données nominatives ;
- les tableaux de bord Power BI internes.

## Orchestration observée dans la V1

Deux ensembles Docker distincts apparaissent dans le kit historique :

1. un service de mise à jour des CV (`maj_cv`) qui récupère les nouveaux stagiaires/formateurs puis crée un fichier de verrouillage lorsque les acquisitions sont terminées ;
2. un service OCR (`ocr_cv`) qui attend ce verrou avant de démarrer le traitement documentaire ;
3. un worker séparé de centralisation Data qui enchaîne les exports Quest, NoCRM, le compactage Beetween puis la publication des fichiers vers OneDrive.

Le dépôt public remplace ce couplage par une CLI déterministe et des services Docker plus petits. La synchronisation distante est placée derrière un profil optionnel et toutes les configurations sensibles passent par variables d'environnement.

## Docker public reconstruit

Le `docker-compose-final.yml` historique fourni référence deux images (`api_mysql` et `ocr_cv`) mais leurs Dockerfiles/requirements correspondants n'étaient pas présents dans le kit final. Cela n'empêche pas de comprendre leurs responsabilités : les imports du worker de mise à jour couvrent notamment HTTP, pandas, SQLAlchemy et monitoring, tandis que le worker OCR requiert Tesseract, Pillow, `pdf2image`, Poppler et LibreOffice.

Les Dockerfiles de ce dépôt sont donc **des reconstructions publiques**, et non une copie prétendument exacte des images de production. Le Dockerfile OneDrive fourni séparément a également été remplacé par une image moderne et générique qui lit les secrets depuis l'environnement.
