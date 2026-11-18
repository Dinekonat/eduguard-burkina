# « On ne développe pas, on se développe »
# — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo

"""
ÉTAPE 3 — TRANSFORMATION
Création du dataset maître : région × année × indicateurs
Calcul des variables dérivées utiles pour le Défi 1 (décrochage scolaire)
"""

import pandas as pd
import numpy as np
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

NETTOYE = r'c:\Users\Lenovo\Desktop\EduGard\02_nettoyage'
SORTIE  = r'c:\Users\Lenovo\Desktop\EduGard\03_transformation'
os.makedirs(SORTIE, exist_ok=True)

ANNEES_SCOLAIRES = [
    '2015-16', '2016-17', '2017-18', '2018-19', '2019-20',
    '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
]

REGIONS_13 = [
    'BOUCLE DU MOUHOUN', 'CASCADES', 'CENTRE', 'CENTRE-EST',
    'CENTRE-NORD', 'CENTRE-OUEST', 'CENTRE-SUD', 'EST',
    'HAUTS-BASSINS', 'NORD', 'PLATEAU CENTRAL', 'SAHEL', 'SUD-OUEST'
]

# ============================================================
# 1. CHARGER LES FICHIERS NETTOYES
# ============================================================

def lire(fichier):
    return pd.read_csv(os.path.join(NETTOYE, fichier), encoding='utf-8-sig')

tap  = lire('EduDataFaso_02-nettoyage_D1_engineer_tap-primaire-par-region_v1.csv')
tbs  = lire('EduDataFaso_02-nettoyage_D1_engineer_tbs-primaire-par-region_v1.csv')
tba  = lire('EduDataFaso_02-nettoyage_D1_engineer_tba-primaire-par-region_v1.csv')
ips_tap = lire('EduDataFaso_02-nettoyage_D1_engineer_ips-tap_v1.csv')
ips_tbs = lire('EduDataFaso_02-nettoyage_D1_engineer_ips-tbs_v1.csv')
cp1  = lire('EduDataFaso_02-nettoyage_D1_engineer_nouveaux-inscrits-cp1_v1.csv')
eff  = lire('EduDataFaso_02-nettoyage_D1_engineer_effectifs-primaire-par-region_v1.csv')
ecoles = lire('EduDataFaso_02-nettoyage_D1_engineer_nombre-ecoles_v1.csv')
cep  = lire('EduDataFaso_02-nettoyage_D1_engineer_taux-reussite-cep_v1.csv')

print("Fichiers chargés ✓")

# ============================================================
# 2. CONSTRUIRE LE DATASET MAITRE (format long : une ligne = région × année)
# ============================================================

lignes = []

for region in REGIONS_13:
    for i, annee in enumerate(ANNEES_SCOLAIRES):

        ligne = {'REGION': region, 'ANNEE': annee}

        # --- TAP (Taux d'Achèvement Primaire) ---
        col_t = f'{annee}_T'
        col_g = f'{annee}_G'
        col_f = f'{annee}_F'

        r_tap = tap[tap['REGION'] == region]
        if not r_tap.empty and col_t in tap.columns:
            ligne['TAP_total']   = pd.to_numeric(r_tap[col_t].values[0], errors='coerce')
            ligne['TAP_garcons'] = pd.to_numeric(r_tap[col_g].values[0], errors='coerce') if col_g in tap.columns else np.nan
            ligne['TAP_filles']  = pd.to_numeric(r_tap[col_f].values[0], errors='coerce') if col_f in tap.columns else np.nan
        else:
            ligne['TAP_total'] = ligne['TAP_garcons'] = ligne['TAP_filles'] = np.nan

        # --- TBS (Taux Brut de Scolarisation) ---
        r_tbs = tbs[tbs['REGION'] == region]
        if not r_tbs.empty and col_t in tbs.columns:
            ligne['TBS_total']   = pd.to_numeric(r_tbs[col_t].values[0], errors='coerce')
            ligne['TBS_garcons'] = pd.to_numeric(r_tbs[col_g].values[0], errors='coerce') if col_g in tbs.columns else np.nan
            ligne['TBS_filles']  = pd.to_numeric(r_tbs[col_f].values[0], errors='coerce') if col_f in tbs.columns else np.nan
        else:
            ligne['TBS_total'] = ligne['TBS_garcons'] = ligne['TBS_filles'] = np.nan

        # --- TBA (Taux Brut d'Admission) ---
        r_tba = tba[tba['REGION'] == region]
        if not r_tba.empty and col_t in tba.columns:
            ligne['TBA_total']   = pd.to_numeric(r_tba[col_t].values[0], errors='coerce')
        else:
            ligne['TBA_total'] = np.nan

        # --- IPS du TAP ---
        col_ips = annee
        r_ips_tap = ips_tap[ips_tap['REGION'] == region]
        if not r_ips_tap.empty and col_ips in ips_tap.columns:
            ligne['IPS_TAP'] = pd.to_numeric(r_ips_tap[col_ips].values[0], errors='coerce')
        else:
            ligne['IPS_TAP'] = np.nan

        # --- IPS du TBS ---
        r_ips_tbs = ips_tbs[ips_tbs['REGION'] == region]
        if not r_ips_tbs.empty and col_ips in ips_tbs.columns:
            ligne['IPS_TBS'] = pd.to_numeric(r_ips_tbs[col_ips].values[0], errors='coerce')
        else:
            ligne['IPS_TBS'] = np.nan

        # --- Nouveaux inscrits CP1 ---
        r_cp1 = cp1[(cp1['REGION'] == region) & (cp1['SEXE'] == 'TOTAL')]
        # Mapper annee scolaire vers colonne effectifs (format 2015-2016)
        annee_long = annee.replace('-', '-20').replace('20-20', '-20')  # 2015-16 → 2015-2016
        # Construction manuelle du mapping
        mapping_annees = {
            '2015-16': '2015-2016', '2016-17': '2016-2017', '2017-18': '2017-2018',
            '2018-19': '2018-2019', '2019-20': '2019-2020', '2020-21': '2020-2021',
            '2021-22': '2021-2022', '2022-23': '2022-2023', '2023-24': '2023-2024',
            '2024-25': '2024-2025'
        }
        col_eff = mapping_annees.get(annee, annee)
        if not r_cp1.empty and col_eff in cp1.columns:
            ligne['CP1_total'] = pd.to_numeric(r_cp1[col_eff].values[0], errors='coerce')
        else:
            ligne['CP1_total'] = np.nan

        # --- Effectifs totaux ---
        r_eff = eff[(eff['REGION'] == region) & (eff['SEXE'] == 'TOTAL')]
        if not r_eff.empty and col_eff in eff.columns:
            ligne['EFFECTIFS_total'] = pd.to_numeric(r_eff[col_eff].values[0], errors='coerce')
        else:
            ligne['EFFECTIFS_total'] = np.nan

        # --- Nombre d'écoles (Total) ---
        r_ec = ecoles[(ecoles['REGION'] == region) & (ecoles['STATUT'] == 'TOTAL')]
        col_ec = col_eff.replace('-', '/')  # 2015-2016 → 2015/2016
        if r_ec.empty:
            # Try uppercase
            r_ec = ecoles[(ecoles['REGION'] == region) & (ecoles['STATUT'].str.upper() == 'TOTAL')]
        if not r_ec.empty and col_ec in ecoles.columns:
            ligne['NB_ECOLES'] = pd.to_numeric(r_ec[col_ec].values[0], errors='coerce')
        elif not r_ec.empty:
            # Try alternate column name format
            col_ec2 = col_eff
            if col_ec2 in ecoles.columns:
                ligne['NB_ECOLES'] = pd.to_numeric(r_ec[col_ec2].values[0], errors='coerce')
            else:
                ligne['NB_ECOLES'] = np.nan
        else:
            ligne['NB_ECOLES'] = np.nan

        # --- Taux de réussite CEP ---
        r_cep = cep[(cep['REGION'] == region) & (cep['SEXE'].str.upper() == 'TOTAL')]
        # CEP années = 2016, 2017, ... (année civile = fin de l'année scolaire)
        annee_cep = str(int('20' + annee.split('-')[1]))
        if not r_cep.empty and annee_cep in cep.columns:
            ligne['CEP_total'] = pd.to_numeric(r_cep[annee_cep].values[0], errors='coerce')
        else:
            ligne['CEP_total'] = np.nan

        lignes.append(ligne)

master = pd.DataFrame(lignes)
print(f"Dataset maître construit : {master.shape[0]} lignes × {master.shape[1]} colonnes")
print(master.head())

# ============================================================
# 3. VARIABLES DERIVEES
# ============================================================

# --- TAUX D'ABANDON (proxy) ---
# Si TAP = 55%, ça veut dire que 45% abandonnent avant la fin du primaire
master['TAUX_ABANDON'] = 100 - master['TAP_total']

# --- ECART DE PARITE FILLES/GARCONS dans le TAP ---
# IPS_TAP < 1 → les garçons achèvent plus que les filles
# IPS_TAP > 1 → les filles achèvent plus que les garçons
master['ECART_PARITE_TAP'] = master['IPS_TAP'] - 1

# --- EVOLUTION DU TAP (variation annuelle) ---
master = master.sort_values(['REGION', 'ANNEE']).reset_index(drop=True)
master['TAP_variation'] = master.groupby('REGION')['TAP_total'].diff()

# --- TENDANCE RECENTE (3 dernières années disponibles) ---
# Pente linéaire simple sur les 3 dernières années
def tendance(serie):
    vals = serie.dropna().values
    if len(vals) < 2:
        return np.nan
    x = np.arange(len(vals))
    return np.polyfit(x, vals, 1)[0]

tendances = master.groupby('REGION')['TAP_total'].apply(tendance).reset_index()
tendances.columns = ['REGION', 'TAP_tendance']
master = master.merge(tendances, on='REGION', how='left')

print("\nVariables dérivées calculées ✓")
print(master[['REGION','ANNEE','TAP_total','TAUX_ABANDON','IPS_TAP','TAP_variation']].tail(20).to_string())

# Sauvegarder le dataset maître
master.to_csv(os.path.join(SORTIE, 'EduDataFaso_03-transformation_D1_engineer_dataset-maitre_v1.csv'),
              index=False, encoding='utf-8-sig')
print("\n[OK] Dataset maître sauvegardé")

# ============================================================
# 4. INDICE DE VULNERABILITE (Niveau 1)
# Score composite par région, basé sur la DERNIERE année disponible
# ============================================================

derniere_annee = '2024-25'
df_last = master[master['ANNEE'] == derniere_annee].copy()

# Indicateurs utilisés et leur poids
# TAP faible → risque élevé (poids fort)
# TBS faible → risque élevé
# IPS_TAP faible (<1) → inégalité fille/garçon → risque
# TAP_tendance négative → la situation empire → risque

def normaliser_inverse(serie):
    """Normalise 0-1, et INVERSE : valeur faible → score élevé (= plus risqué)"""
    mn, mx = serie.min(), serie.max()
    if mx == mn:
        return pd.Series([0.5] * len(serie), index=serie.index)
    return 1 - (serie - mn) / (mx - mn)

def normaliser_direct(serie):
    """Normalise 0-1, valeur élevée → score élevé"""
    mn, mx = serie.min(), serie.max()
    if mx == mn:
        return pd.Series([0.5] * len(serie), index=serie.index)
    return (serie - mn) / (mx - mn)

# Scores individuels (sur les régions ayant des données)
df_idx = df_last[['REGION', 'TAP_total', 'TBS_total', 'IPS_TAP', 'TAP_tendance']].copy()
df_idx = df_idx.set_index('REGION')

scores = pd.DataFrame(index=df_idx.index)

if df_idx['TAP_total'].notna().sum() > 1:
    scores['score_TAP']       = normaliser_inverse(df_idx['TAP_total'])          # TAP bas → risque haut
if df_idx['TBS_total'].notna().sum() > 1:
    scores['score_TBS']       = normaliser_inverse(df_idx['TBS_total'])          # TBS bas → risque haut
if df_idx['IPS_TAP'].notna().sum() > 1:
    scores['score_IPS']       = normaliser_inverse(df_idx['IPS_TAP'].abs())      # Inégalité → risque
if df_idx['TAP_tendance'].notna().sum() > 1:
    scores['score_tendance']  = normaliser_inverse(df_idx['TAP_tendance'])       # Tendance basse → risque

# Poids des indicateurs
poids = {'score_TAP': 0.40, 'score_TBS': 0.25, 'score_IPS': 0.15, 'score_tendance': 0.20}

scores['INDICE_VULNERABILITE'] = sum(
    scores[c] * poids[c] for c in poids if c in scores.columns
)

# Classer en 3 niveaux
def niveau_risque(val):
    if pd.isna(val): return 'Inconnu'
    if val >= 0.65: return 'Élevé'
    if val >= 0.35: return 'Modéré'
    return 'Faible'

scores['NIVEAU_RISQUE'] = scores['INDICE_VULNERABILITE'].apply(niveau_risque)
scores['RANG'] = scores['INDICE_VULNERABILITE'].rank(ascending=False).astype(int)
scores = scores.sort_values('RANG').reset_index()

print("\n=== INDICE DE VULNERABILITE PAR REGION (2024-25) ===")
print(scores[['REGION','INDICE_VULNERABILITE','NIVEAU_RISQUE','RANG']].to_string(index=False))

scores.to_csv(os.path.join(SORTIE, 'EduDataFaso_03-transformation_D1_analyst_indice-vulnerabilite_v1.csv'),
              index=False, encoding='utf-8-sig')

# Sauvegarder aussi le dataset maître complet avec l'indice
master_complet = master.merge(
    scores[['REGION','INDICE_VULNERABILITE','NIVEAU_RISQUE','RANG']],
    on='REGION', how='left'
)
master_complet.to_csv(
    os.path.join(SORTIE, 'EduDataFaso_03-transformation_D1_engineer_dataset-complet_v1.csv'),
    index=False, encoding='utf-8-sig'
)

print("\n[OK] Indice de vulnérabilité sauvegardé")
print(f"\nFichiers dans 03_transformation :")
for f in sorted(os.listdir(SORTIE)):
    print(f"  {f}")
