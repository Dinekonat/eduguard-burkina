# « On ne développe pas, on se développe »
# — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo

"""
Script d'interrogation de l'IA — EduGuard
Utilise l'API Gemini (Google) pour analyser les données éducatives
et répondre à des questions sur le décrochage scolaire au Burkina Faso.

Usage :
    python script_ia_eduguard.py

Prérequis :
    pip install google-generativeai pandas
    Créer une clé API gratuite sur : https://aistudio.google.com/app/apikey
"""

import google.generativeai as genai
import pandas as pd
import os
import json

# ─── CONFIGURATION ─────────────────────────────────────────
# Remplace par ta clé API Gemini (gratuite sur aistudio.google.com)
API_KEY = "COLLE_TA_CLE_API_ICI"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ─── CHARGEMENT DES DONNÉES ─────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

indice = pd.read_csv(
    os.path.join(BASE, '03_transformation',
                 'EduDataFaso_03-transformation_D1_analyst_indice-vulnerabilite_v1.csv'),
    encoding='utf-8-sig'
)

master = pd.read_csv(
    os.path.join(BASE, '03_transformation',
                 'EduDataFaso_03-transformation_D1_engineer_dataset-maitre_v1.csv'),
    encoding='utf-8-sig'
)

# ─── CONTEXTE ENVOYÉ À L'IA ─────────────────────────────────
def construire_contexte():
    """Prépare le résumé des données à envoyer à l'IA."""

    # Résumé de l'indice de vulnérabilité
    indice_str = indice[['REGION','INDICE_VULNERABILITE','NIVEAU_RISQUE','RANG']].to_string(index=False)

    # Statistiques TAP 2024-25
    df_2425 = master[master['ANNEE'] == '2024-25'][['REGION','TAP_total','TAUX_ABANDON','IPS_TAP']]
    stats_str = df_2425.to_string(index=False)

    contexte = f"""
Tu es un expert en éducation et analyse de données pour le Burkina Faso.
Tu travailles sur le projet EduGuard dans le cadre du Data Challenge Burkina 2026.

DONNÉES DISPONIBLES :

1. Indice de vulnérabilité au décrochage scolaire par région (2024-25) :
{indice_str}

2. Indicateurs clés par région (année scolaire 2024-25) :
   TAP = Taux d'Achèvement Primaire (%), TAUX_ABANDON = 100 - TAP, IPS_TAP = Indice Parité Sexes
{stats_str}

DÉFINITIONS IMPORTANTES :
- TAP (Taux d'Achèvement Primaire) : % d'élèves qui terminent le primaire
- TAUX_ABANDON estimé : 100% - TAP (estimation du décrochage)
- IPS_TAP : ratio filles/garçons dans l'achèvement (>1 = filles mieux, <1 = garçons mieux)
- Indice de vulnérabilité : score 0-1 (plus élevé = plus à risque)

Réponds en français, de façon claire et concise, en te basant uniquement sur ces données.
"""
    return contexte


# ─── QUESTIONS PRÉDÉFINIES (pour la documentation) ──────────
QUESTIONS_DOC = [
    "Quelles sont les 3 régions les plus à risque de décrochage scolaire et pourquoi ?",
    "Que révèle la comparaison entre la région du Sahel et la région du Centre ?",
    "Comment interpréter l'indice de parité des sexes dans le contexte du décrochage scolaire ?",
    "Quelles actions concrètes recommandes-tu pour réduire le décrochage dans les régions à risque élevé ?",
    "Quelles sont les limites de cet indice de vulnérabilité ?",
]


def interroger_ia(question, contexte):
    """Envoie une question à l'IA avec le contexte des données."""
    prompt = f"{contexte}\n\nQUESTION : {question}\n\nRÉPONSE :"
    response = model.generate_content(prompt)
    return response.text


def mode_documentation():
    """Génère les réponses aux questions prédéfinies pour la documentation."""
    contexte = construire_contexte()
    resultats = []

    print("=" * 65)
    print("EduGuard — Analyse IA des données éducatives")
    print("Modèle : Gemini 1.5 Flash (Google)")
    print("=" * 65)
    print()

    for i, question in enumerate(QUESTIONS_DOC, 1):
        print(f"Q{i} : {question}")
        print("-" * 50)
        reponse = interroger_ia(question, contexte)
        print(reponse)
        print()
        resultats.append({
            "question": question,
            "reponse": reponse,
            "modele": "gemini-1.5-flash"
        })

    # Sauvegarder les résultats
    sortie = os.path.join(BASE, '04_analyse')
    os.makedirs(sortie, exist_ok=True)
    with open(os.path.join(sortie, 'EduDataFaso_04-analyse_D1_scientist_analyse-ia_v1.json'),
              'w', encoding='utf-8') as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print("[OK] Résultats sauvegardés dans 04_analyse/")
    return resultats


def mode_interactif():
    """Mode chat : pose tes propres questions."""
    contexte = construire_contexte()
    print("=" * 65)
    print("EduGuard — Chat IA interactif")
    print("Tape 'quitter' pour arrêter.")
    print("=" * 65)
    print()

    while True:
        question = input("Ta question : ").strip()
        if question.lower() in ['quitter', 'exit', 'q']:
            break
        if not question:
            continue
        print()
        reponse = interroger_ia(question, contexte)
        print(f"IA : {reponse}")
        print()


# ─── POINT D'ENTRÉE ─────────────────────────────────────────
if __name__ == "__main__":
    print("\nChoisir le mode :")
    print("  1 → Générer l'analyse complète pour la documentation")
    print("  2 → Mode chat interactif")
    choix = input("\nTon choix (1 ou 2) : ").strip()

    if choix == "2":
        mode_interactif()
    else:
        mode_documentation()
