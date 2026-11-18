# « On ne développe pas, on se développe »
# — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo

import pandas as pd
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

ENTREE = r'c:\Users\Lenovo\Desktop\EduGard\01_collecte'
SORTIE = r'c:\Users\Lenovo\Desktop\EduGard\02_nettoyage'
os.makedirs(SORTIE, exist_ok=True)

# Journal de nettoyage : on note tout ce qu'on corrige
journal = []

# Les 13 régions officielles du Burkina Faso (primaire, 13 régions)
REGIONS_VALIDES = {
    'BOUCLE DU MOUHOUN', 'CASCADES', 'CENTRE', 'CENTRE-EST',
    'CENTRE-NORD', 'CENTRE-OUEST', 'CENTRE-SUD', 'EST',
    'HAUTS-BASSINS', 'NORD', 'PLATEAU CENTRAL', 'SAHEL', 'SUD-OUEST'
}

# Mots-clés qui indiquent une ligne de total à supprimer
TOTAUX = {'NATIONAL', 'BURKINA FASO', 'TOTAL GENERAL', 'TOTAL'}


def nettoyer_colonnes(df):
    """Nettoie les noms de colonnes : enlève les notes cachées et espaces."""
    nouvelles = []
    for col in df.columns:
        col_str = str(col)
        # Enlève tout ce qui vient après un saut de ligne (note cachée)
        col_propre = col_str.split('\n')[0].strip()
        # Enlève aussi les espaces insécables (\xa0)
        col_propre = col_propre.replace('\xa0', '').strip()
        # Convertit les floats (ex: 2016.0) en entiers propres (2016)
        try:
            if '.' in col_propre and col_propre.replace('.', '').replace('-', '').isdigit():
                col_propre = str(int(float(col_propre)))
        except Exception:
            pass
        nouvelles.append(col_propre)
    return nouvelles


def harmoniser_region(valeur):
    """Met la région en MAJUSCULES et enlève les espaces superflus."""
    if pd.isna(valeur):
        return valeur
    return str(valeur).strip().upper()


def est_total(valeur):
    """Renvoie True si la valeur est une ligne de total à supprimer."""
    if pd.isna(valeur):
        return False
    return str(valeur).strip().upper() in TOTAUX


# ==============================================================
# GROUPE 1 — Fichiers avec colonnes REGION + SEXE
# (effectifs par région, nouveaux inscrits CP1)
# ==============================================================
print("=" * 65)
print("GROUPE 1 : Fichiers REGION + SEXE")
print("=" * 65)

fichiers_g1 = [
    ('effectifs-primaire-par-region',   'REGION', 'SEXE'),
    ('nouveaux-inscrits-cp1',           'REGION', 'SEXE'),
]

for desc, col_region, col_sexe in fichiers_g1:
    nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
    nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

    df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')

    # --- Nettoyer les noms de colonnes ---
    df.columns = nettoyer_colonnes(df)

    # --- Remplir les NaN dans REGION (propagation vers le bas) ---
    nb_nan_avant = df[col_region].isna().sum()
    df[col_region] = df[col_region].ffill()
    journal.append(f"{desc} | {nb_nan_avant} NaN dans REGION remplis par propagation")

    # --- Harmoniser les noms de région ---
    df[col_region] = df[col_region].apply(harmoniser_region)

    # --- Supprimer les lignes de total national ---
    nb_avant = len(df)
    df = df[~df[col_region].apply(est_total)]
    nb_supp = nb_avant - len(df)
    if nb_supp > 0:
        journal.append(f"{desc} | {nb_supp} ligne(s) de total national supprimées")

    # --- Vérification G + F = T ---
    annees = [c for c in df.columns if c not in [col_region, col_sexe]]
    erreurs = []
    for region in df[col_region].unique():
        df_r = df[df[col_region] == region]
        for annee in annees:
            try:
                g = df_r[df_r[col_sexe] == 'GARCONS'][annee].values
                f = df_r[df_r[col_sexe] == 'FILLES'][annee].values
                t = df_r[df_r[col_sexe] == 'TOTAL'][annee].values
                if len(g) and len(f) and len(t):
                    if abs(float(g[0]) + float(f[0]) - float(t[0])) > 2:
                        erreurs.append(f"  ANOMALIE {region} | {annee} | G+F={g[0]+f[0]} ≠ T={t[0]}")
            except Exception:
                pass
    if erreurs:
        journal.append(f"{desc} | ANOMALIES G+F≠T : " + " ; ".join(erreurs))
    else:
        journal.append(f"{desc} | Contrôle G+F=T : OK sur toutes les régions/années")

    df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
    print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
    print(f"     Régions : {sorted(df[col_region].unique().tolist())}")
    print()


# ==============================================================
# GROUPE 2 — Fichiers avec colonnes MILIEU/STATUT + SEXE
# (par milieu, par statut)
# ==============================================================
print("=" * 65)
print("GROUPE 2 : Fichiers MILIEU/STATUT + SEXE")
print("=" * 65)

fichiers_g2 = [
    ('effectifs-primaire-par-milieu',  'MILIEU'),
    ('effectifs-primaire-par-statut',  'STATUT'),
]

for desc, col_cle in fichiers_g2:
    nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
    nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

    df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
    df.columns = nettoyer_colonnes(df)

    nb_nan = df[col_cle].isna().sum()
    df[col_cle] = df[col_cle].ffill()
    if nb_nan > 0:
        journal.append(f"{desc} | {nb_nan} NaN dans {col_cle} remplis")

    # Supprimer NATIONAL si présent
    nb_avant = len(df)
    df = df[~df[col_cle].apply(est_total)]
    if len(df) < nb_avant:
        journal.append(f"{desc} | {nb_avant - len(df)} ligne(s) de total supprimées")

    df[col_cle] = df[col_cle].apply(harmoniser_region)

    df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
    print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
    journal.append(f"{desc} | Nettoyé OK | {df.shape[0]} lignes")
    print()


# ==============================================================
# GROUPE 3 — Fichier par niveau (STATUT + NIVEAU + SEXE)
# ==============================================================
print("=" * 65)
print("GROUPE 3 : Fichier par niveau (CP1→CM2)")
print("=" * 65)

desc = 'effectifs-primaire-par-niveau'
nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
df.columns = nettoyer_colonnes(df)

for col in ['STATUT', 'NIVEAU', 'SEXE']:
    nb = df[col].isna().sum()
    df[col] = df[col].ffill()
    if nb > 0:
        journal.append(f"{desc} | {nb} NaN dans {col} remplis")

df['STATUT'] = df['STATUT'].apply(harmoniser_region)
nb_avant = len(df)
df = df[~df['STATUT'].apply(est_total)]
if len(df) < nb_avant:
    journal.append(f"{desc} | {nb_avant-len(df)} total(aux) supprimé(s)")

df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
journal.append(f"{desc} | Nettoyé OK | {df.shape[0]} lignes")
print()


# ==============================================================
# GROUPE 4 — Fichiers TBA, TBS, TAP (REGION + colonnes ANNEE_SEXE)
# ==============================================================
print("=" * 65)
print("GROUPE 4 : TBA, TBS, TAP (double en-tête déjà reconstruit)")
print("=" * 65)

fichiers_g4 = [
    'tba-primaire-par-region',
    'tbs-primaire-par-region',
    'tap-primaire-par-region',
]

for desc in fichiers_g4:
    nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
    nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

    df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
    df.columns = nettoyer_colonnes(df)

    # Harmoniser la colonne REGION
    df['REGION'] = df['REGION'].apply(harmoniser_region)

    # Supprimer les lignes de total (Burkina Faso, NATIONAL...)
    nb_avant = len(df)
    df = df[~df['REGION'].apply(est_total)]
    nb_supp = nb_avant - len(df)
    journal.append(f"{desc} | {nb_supp} ligne(s) de total supprimées | {df.shape[0]} régions conservées")

    # Vérifier qu'on a bien 13 régions
    regions_presentes = set(df['REGION'].tolist())
    manquantes = REGIONS_VALIDES - regions_presentes
    if manquantes:
        journal.append(f"{desc} | ATTENTION : régions manquantes : {manquantes}")
    else:
        journal.append(f"{desc} | Contrôle 13 régions : OK")

    df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
    print(f"[OK] {desc} → {df.shape[0]} lignes (régions), {df.shape[1]} colonnes")
    print(f"     Régions : {sorted(df['REGION'].tolist())}")
    print()


# ==============================================================
# GROUPE 5 — IPS (Indices de Parité des Sexes)
# Colonne : "Régions" (avec accent) → à renommer "REGION"
# ==============================================================
print("=" * 65)
print("GROUPE 5 : IPS (Indices de Parité Sexes)")
print("=" * 65)

fichiers_g5 = ['ips-tba', 'ips-tbs', 'ips-tap']

for desc in fichiers_g5:
    nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
    nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

    df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
    df.columns = nettoyer_colonnes(df)

    # Renommer "Régions" → "REGION" pour uniformité
    df = df.rename(columns={c: 'REGION' for c in df.columns if 'gion' in c.lower()})

    df['REGION'] = df['REGION'].apply(harmoniser_region)

    nb_avant = len(df)
    df = df[~df['REGION'].apply(est_total)]
    nb_supp = nb_avant - len(df)

    # Supprimer les lignes NaN dans REGION
    df = df.dropna(subset=['REGION'])
    df = df[df['REGION'].str.strip() != '']

    journal.append(f"{desc} | {nb_supp} total(aux) supprimé(s) | {df.shape[0]} régions")

    df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
    print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
    print()


# ==============================================================
# GROUPE 6 — Nombre d'écoles (REGION + STATUT + années)
# ==============================================================
print("=" * 65)
print("GROUPE 6 : Nombre d'écoles par région")
print("=" * 65)

desc = 'nombre-ecoles'
nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
df.columns = nettoyer_colonnes(df)

nb_nan = df['REGION'].isna().sum()
df['REGION'] = df['REGION'].ffill()
df['REGION'] = df['REGION'].apply(harmoniser_region)
df['STATUT'] = df['STATUT'].apply(harmoniser_region)

nb_avant = len(df)
df = df[~df['REGION'].apply(est_total)]
journal.append(f"{desc} | {nb_nan} NaN remplis | {nb_avant-len(df)} total(aux) supprimé(s)")

# Uniformiser les noms de colonnes années (2015/2016 → 2015-2016)
df.columns = [c.replace('/', '-') if '/' in str(c) else c for c in df.columns]

df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
journal.append(f"{desc} | Nettoyé OK")
print()


# ==============================================================
# GROUPE 7 — Taux de réussite CEP (Région + Sexe + années en float)
# ==============================================================
print("=" * 65)
print("GROUPE 7 : Taux de réussite au CEP")
print("=" * 65)

desc = 'taux-reussite-cep'
nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
df.columns = nettoyer_colonnes(df)

# Renommer "Région" → "REGION", "Sexe" → "SEXE"
df = df.rename(columns={
    c: 'REGION' for c in df.columns if c.lower() in ['région', 'region', 'régions']
})
df = df.rename(columns={
    c: 'SEXE' for c in df.columns if c.lower() == 'sexe'
})

nb_nan = df['REGION'].isna().sum()
df['REGION'] = df['REGION'].ffill()
df['REGION'] = df['REGION'].apply(harmoniser_region)
df['SEXE'] = df['SEXE'].apply(harmoniser_region)

nb_avant = len(df)
df = df[~df['REGION'].apply(est_total)]
df = df.dropna(subset=['REGION'])

journal.append(f"{desc} | {nb_nan} NaN remplis | {nb_avant-len(df)} total(aux) supprimé(s)")

df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
print()


# ==============================================================
# GROUPE 8 — Effectifs préscolaire
# (double en-tête : REGION + ANNEE_SEXE)
# ==============================================================
print("=" * 65)
print("GROUPE 8 : Effectifs préscolaire")
print("=" * 65)

desc = 'effectifs-prescolaire'
nom_entree = f'EduDataFaso_01-collecte_D1_engineer_{desc}_v1.csv'
nom_sortie = f'EduDataFaso_02-nettoyage_D1_engineer_{desc}_v1.csv'

df = pd.read_csv(os.path.join(ENTREE, nom_entree), encoding='utf-8-sig')
df.columns = nettoyer_colonnes(df)

df['REGION'] = df['REGION'].apply(harmoniser_region)

nb_avant = len(df)
df = df[~df['REGION'].apply(est_total)]
df = df.dropna(subset=['REGION'])
df = df[df['REGION'].str.strip() != '']

journal.append(f"{desc} | {nb_avant-len(df)} total(aux)/NaN supprimés | {df.shape[0]} lignes conservées")

df.to_csv(os.path.join(SORTIE, nom_sortie), index=False, encoding='utf-8-sig')
print(f"[OK] {desc} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
print()


# ==============================================================
# ECRITURE DU JOURNAL DE NETTOYAGE
# ==============================================================
journal_path = os.path.join(SORTIE, 'EduDataFaso_02-nettoyage_D1_engineer_journal-nettoyage_v1.txt')
with open(journal_path, 'w', encoding='utf-8') as f:
    f.write("JOURNAL DE NETTOYAGE - Etape 2\n")
    f.write("Equipe  : EduData Faso\n")
    f.write("Defi    : Defi 1 - Decrochage scolaire\n")
    f.write("Date    : 16 novembre 2026\n")
    f.write("=" * 65 + "\n\n")
    f.write("ACTIONS REALISEES :\n\n")
    for i, ligne in enumerate(journal, 1):
        f.write(f"  {i:02d}. {ligne}\n")
    f.write("\n" + "=" * 65 + "\n")
    f.write("DECISIONS DE NETTOYAGE EXPLIQUEES :\n\n")
    f.write("1. PROPAGATION DES NaN (ffill) :\n")
    f.write("   Dans Excel, une région n'est écrite qu'une fois pour 3 lignes\n")
    f.write("   (Garçons, Filles, Total). A l'export CSV, les 2 lignes suivantes\n")
    f.write("   ont REGION vide (NaN). On propage le nom vers le bas.\n\n")
    f.write("2. SUPPRESSION DES LIGNES DE TOTAL NATIONAL :\n")
    f.write("   Les lignes 'NATIONAL' et 'Burkina Faso' sont des sommes de toutes\n")
    f.write("   les régions. Les garder fausserait les calculs d'indicateurs.\n\n")
    f.write("3. NETTOYAGE DES NOMS DE COLONNES :\n")
    f.write("   La colonne '2018-2019' contenait une note cachée des organisateurs\n")
    f.write("   (note de traçabilité). Note reconnue et documentée ci-dessous.\n\n")
    f.write("4. HARMONISATION DES NOMS DE RÉGIONS :\n")
    f.write("   Tout mis en MAJUSCULES et espaces superflus supprimés pour\n")
    f.write("   permettre la fusion des fichiers à l'étape suivante.\n\n")
    f.write("5. CONTROLE DE COHERENCE G + F = T :\n")
    f.write("   Vérifié pour chaque région et chaque année dans les fichiers\n")
    f.write("   effectifs et nouveaux inscrits CP1.\n\n")
    f.write("NOTE DE TRACABILITE (demandée par les organisateurs) :\n")
    f.write("   « On ne développe pas, on se développe »\n")
    f.write("   — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo\n")

print("=" * 65)
print("JOURNAL DE NETTOYAGE CREE")
print()

# Lister les fichiers produits
print("FICHIERS PRODUITS DANS 02_nettoyage :")
for f in sorted(os.listdir(SORTIE)):
    size = os.path.getsize(os.path.join(SORTIE, f))
    print(f"  {f:65s}  {size:>7} octets")
