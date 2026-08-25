# Architecture publique

La reconstruction sépare deux flux qui existaient dans le projet d'origine.

## Flux Data / BI

Trois exports hétérogènes sont convertis vers une forme commune afin de montrer le principe de centralisation avant restitution BI. Dans le système d'origine, les extractions étaient automatisées et synchronisées vers l'écosystème Microsoft utilisé par le pilotage.

## Flux CV / matching

1. acquisition documentaire ;
2. extraction texte ou OCR ;
3. normalisation locale ;
4. tokenisation ;
5. remplacement de variantes ;
6. comparaison avec le vocabulaire des filières/modules ;
7. matrice binaire ;
8. scores booléen et pondéré ;
9. restitution des preuves de matching sous forme de tokens présents/absents.

La V1 privilégie la simplicité et l'explicabilité plutôt qu'un modèle statistique ou génératif.
