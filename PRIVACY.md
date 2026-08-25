# Privacy & Data Governance

Ce dépôt public est conçu pour **ne contenir aucune donnée personnelle issue du projet d'origine**.

## Données incluses

Uniquement des données synthétiques créées pour la démonstration :

- `Candidate_001`, `Candidate_002`, `Candidate_003` ;
- filières/modules fictifs ;
- identifiants fictifs `CAND-*`, `SESSION-*`, `LEAD-*`.

## Données volontairement exclues

- CV réels, y compris sous forme OCR, TXT, XLSX ou PDF ;
- noms/prénoms, emails, téléphones, adresses ou identifiants de candidats/formateurs ;
- bases SQLite et matrices réelles ;
- exports Beetween, Quest ou NoCRM ;
- historiques SharePoint / OneDrive ;
- PBIX ou exports Power BI ;
- logs de production ;
- secrets et configurations d'accès.

## Choix d'architecture

Le matching public est entièrement déterministe : aucune requête vers un LLM, aucun embedding et aucun modèle ML. Les scores proviennent uniquement de règles et poids visibles dans le dépôt.

Ce choix ne remplace pas une analyse RGPD/AI Act propre à un déploiement réel. Pour un usage réel, prévoir notamment : finalité documentée, base légale, minimisation, durée de conservation, contrôle des accès, information des personnes, exercice des droits, journalisation et revue humaine appropriée.
