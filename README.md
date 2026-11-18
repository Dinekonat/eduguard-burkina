# EduGuard 🎓

> *« On ne développe pas, on se développe »*
> — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo

**Intelligence artificielle pour anticiper et prévenir le décrochage scolaire au Burkina Faso**

Projet réalisé dans le cadre du **Data Challenge Burkina 2026 — Édition Éducation**
Équipe **EduData Faso** · Défi 1 : Cartographie et anticipation du risque de décrochage scolaire

---

## 🔗 Accès au dashboard

👉 **[Ouvrir EduGuard sur Streamlit Cloud](https://eduguard-burkina.streamlit.app)**

---

## 📊 Résultats clés

| Rang | Région | Risque | Taux d'abandon estimé |
|---|---|---|---|
| 1 | SAHEL | 🔴 Élevé | ~89% |
| 2 | EST | 🔴 Élevé | ~79% |
| 3 | BOUCLE DU MOUHOUN | 🔴 Élevé | ~63% |
| 4-8 | Centre-Nord, Centre-Est, Cascades, Nord, Sud-Ouest | 🟠 Modéré | — |
| 9-13 | Hauts-Bassins → Centre | 🟢 Faible | — |

---

## 🗂️ Structure du projet

```
EduGard/
├── eduguard_app.py              ← Dashboard Streamlit (application principale)
├── script_ia_eduguard.py        ← Script d'interrogation IA (Gemini)
├── nettoyage_complet.py         ← Étape 2 : Nettoyage
├── etape3_transformation.py     ← Étapes 3 & 4 : Transformation + Analyse
├── requirements.txt
├── 01_collecte/                 ← Données brutes exportées (14 CSV)
├── 02_nettoyage/                ← Données nettoyées + journal
├── 03_transformation/           ← Dataset maître + indice de vulnérabilité
└── 04_analyse/                  ← Analyses IA
```

---

## 🚀 Lancer en local

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Exécuter le nettoyage
python nettoyage_complet.py

# 3. Exécuter la transformation
python etape3_transformation.py

# 4. Lancer le dashboard
streamlit run eduguard_app.py
```

---

## 🛠️ Technologies utilisées

| Outil | Rôle |
|---|---|
| Python 3.12 | Langage principal |
| Pandas / NumPy | Nettoyage et transformation des données |
| Scikit-learn | Normalisation et calcul de l'indice |
| Plotly | Graphiques interactifs |
| Streamlit | Interface web du dashboard |
| Gemini API | Analyse IA des résultats |

---

## 📁 Source des données

**DGESS — Direction Générale des Études et des Statistiques Sectorielles**
Ministère de l'Éducation Nationale du Burkina Faso
Période couverte : 2015/2016 → 2024/2025

---

## 🤖 Utilisation de l'IA

Un assistant IA a été utilisé pour structurer les scripts Python de nettoyage et de transformation.
Toutes les décisions analytiques (choix des indicateurs, poids de l'indice, interprétation) ont été revues et validées.
Conformément aux règles du challenge, cette utilisation est déclarée et documentée.

---

*Data Challenge Burkina 2026 · Équipe EduData Faso*
