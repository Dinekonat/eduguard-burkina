# « On ne développe pas, on se développe »
# — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo

"""
EduGuard — Dashboard interactif
Défi 1 : Cartographie et anticipation du risque de décrochage scolaire
Équipe EduData Faso — Data Challenge Burkina 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ─── Configuration de la page ───────────────────────────────
st.set_page_config(
    page_title="EduGuard — Décrochage Scolaire Burkina Faso",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Chemins des données ────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DIR_TRANSFO = os.path.join(BASE, '03_transformation')
DIR_NETTOYE = os.path.join(BASE, '02_nettoyage')

# ─── Chargement des données ─────────────────────────────────
@st.cache_data
def charger_donnees():
    master = pd.read_csv(
        os.path.join(DIR_TRANSFO, 'EduDataFaso_03-transformation_D1_engineer_dataset-complet_v1.csv'),
        encoding='utf-8-sig'
    )
    indice = pd.read_csv(
        os.path.join(DIR_TRANSFO, 'EduDataFaso_03-transformation_D1_analyst_indice-vulnerabilite_v1.csv'),
        encoding='utf-8-sig'
    )
    return master, indice

master, indice = charger_donnees()

# Coordonnées approximatives des 13 régions (centroïdes)
COORDS = {
    'BOUCLE DU MOUHOUN': (12.3, -3.1),
    'CASCADES':          (10.4, -4.5),
    'CENTRE':            (12.4, -1.5),
    'CENTRE-EST':        (11.5, -0.4),
    'CENTRE-NORD':       (13.0, -1.1),
    'CENTRE-OUEST':      (12.1, -2.9),
    'CENTRE-SUD':        (11.5, -1.4),
    'EST':               (12.3,  0.9),
    'HAUTS-BASSINS':     (11.2, -4.2),
    'NORD':              (13.7, -2.2),
    'PLATEAU CENTRAL':   (12.3, -0.8),
    'SAHEL':             (14.0, -0.3),
    'SUD-OUEST':         (10.8, -3.5),
}

COULEURS_RISQUE = {'Élevé': '#d62728', 'Modéré': '#ff7f0e', 'Faible': '#2ca02c', 'Inconnu': '#aec7e8'}
ANNEES = sorted(master['ANNEE'].unique().tolist())

# ─── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Burkina_Faso.svg/320px-Flag_of_Burkina_Faso.svg.png",
             width=120)
    st.title("🎓 EduGuard")
    st.caption("Anticiper le décrochage scolaire")
    st.divider()

    annee_sel = st.selectbox("📅 Année scolaire", ANNEES, index=len(ANNEES)-1)
    regions_sel = st.multiselect(
        "🗺️ Régions à afficher",
        options=sorted(master['REGION'].unique().tolist()),
        default=sorted(master['REGION'].unique().tolist())
    )
    st.divider()
    st.markdown("**Équipe EduData Faso**")
    st.markdown("Défi 1 — Data Challenge Burkina 2026")
    st.markdown("---")
    st.caption("*« On ne développe pas, on se développe »*")
    st.caption("— Joseph Ki-Zerbo")

# ─── DONNÉES FILTRÉES ───────────────────────────────────────
df_annee  = master[(master['ANNEE'] == annee_sel) & (master['REGION'].isin(regions_sel))].copy()
df_indice = indice[indice['REGION'].isin(regions_sel)].copy()

# Ajouter coordonnées
df_indice['LAT'] = df_indice['REGION'].map(lambda r: COORDS.get(r, (12, -1.5))[0])
df_indice['LON'] = df_indice['REGION'].map(lambda r: COORDS.get(r, (12, -1.5))[1])
df_annee['LAT']  = df_annee['REGION'].map(lambda r: COORDS.get(r, (12, -1.5))[0])
df_annee['LON']  = df_annee['REGION'].map(lambda r: COORDS.get(r, (12, -1.5))[1])

# ─── EN-TÊTE ────────────────────────────────────────────────
st.title("🎓 EduGuard — Tableau de bord du décrochage scolaire")
st.caption(f"Burkina Faso · Enseignement primaire · Année scolaire sélectionnée : **{annee_sel}**")
st.divider()

# ─── MÉTRIQUES CLÉS ─────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

nb_eleve  = int(df_annee['EFFECTIFS_total'].sum()) if 'EFFECTIFS_total' in df_annee else 0
tap_moy   = df_annee['TAP_total'].mean()
abandon_moy = df_annee['TAUX_ABANDON'].mean()
nb_risque_eleve = len(df_indice[df_indice['NIVEAU_RISQUE'] == 'Élevé'])

with col1:
    st.metric("👨‍🎓 Élèves (primaire)", f"{nb_eleve:,}".replace(',', ' '))
with col2:
    st.metric("📊 TAP moyen", f"{tap_moy:.1f}%" if not pd.isna(tap_moy) else "N/D",
              delta=None)
with col3:
    st.metric("⚠️ Taux d'abandon moyen", f"{abandon_moy:.1f}%" if not pd.isna(abandon_moy) else "N/D")
with col4:
    st.metric("🔴 Régions à risque élevé", f"{nb_risque_eleve} / {len(regions_sel)}")

st.divider()

# ─── LIGNE 1 : CARTE + CLASSEMENT ───────────────────────────
col_carte, col_class = st.columns([1.6, 1])

with col_carte:
    st.subheader("🗺️ Carte des risques par région")

    if not df_indice.empty:
        df_map = df_indice.copy()
        df_map['LAT'] = df_map['REGION'].map(lambda r: COORDS.get(r, (12, -1.5))[0])
        df_map['LON'] = df_map['REGION'].map(lambda r: COORDS.get(r, (12, -1.5))[1])
        df_map['Abandon_pct'] = (df_map['INDICE_VULNERABILITE'] * 100).round(1)
        df_map['Risque_label'] = df_map['NIVEAU_RISQUE'].map(
            {'Élevé': '🔴 Élevé', 'Modéré': '🟠 Modéré', 'Faible': '🟢 Faible'}
        )

        fig_map = go.Figure()

        for niveau, couleur in [('Élevé', '#d62728'), ('Modéré', '#ff7f0e'), ('Faible', '#2ca02c')]:
            df_n = df_map[df_map['NIVEAU_RISQUE'] == niveau]
            if df_n.empty:
                continue
            fig_map.add_trace(go.Scattergeo(
                lat=df_n['LAT'],
                lon=df_n['LON'],
                mode='markers+text',
                marker=dict(
                    size=df_n['INDICE_VULNERABILITE'] * 50 + 12,
                    color=couleur,
                    opacity=0.85,
                    line=dict(width=1, color='white')
                ),
                text=df_n['REGION'].str.replace(' ', '<br>'),
                textposition='top center',
                textfont=dict(size=9, color='black'),
                name=f'{niveau}',
                hovertemplate=(
                    '<b>%{customdata[0]}</b><br>'
                    'Indice : %{customdata[1]:.3f}<br>'
                    'Rang : #%{customdata[2]}<br>'
                    'Risque : %{customdata[3]}<extra></extra>'
                ),
                customdata=df_n[['REGION', 'INDICE_VULNERABILITE', 'RANG', 'NIVEAU_RISQUE']].values
            ))

        fig_map.update_layout(
            title='Carte des risques de décrochage scolaire — Burkina Faso (2024-25)',
            height=430,
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(title='Niveau de risque', x=0.01, y=0.99),
            geo=dict(
                scope='africa',
                center=dict(lat=12.3, lon=-1.6),
                projection_scale=12,
                showland=True,
                landcolor='#f0ede4',
                showocean=True,
                oceancolor='#cde',
                showcountries=True,
                countrycolor='#aaa',
                showcoastlines=True,
                coastlinecolor='#aaa',
                showlakes=False,
                bgcolor='#f8f9fa',
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour les régions sélectionnées.")

with col_class:
    st.subheader("📋 Classement des régions")
    df_rank = df_indice[['RANG','REGION','INDICE_VULNERABILITE','NIVEAU_RISQUE']].sort_values('RANG')
    df_rank['Risque'] = df_rank['NIVEAU_RISQUE'].map(
        {'Élevé': '🔴 Élevé', 'Modéré': '🟠 Modéré', 'Faible': '🟢 Faible', 'Inconnu': '⚪ Inconnu'}
    )
    df_rank['Indice'] = df_rank['INDICE_VULNERABILITE'].map(lambda x: f"{x:.3f}" if not pd.isna(x) else "N/D")
    st.dataframe(
        df_rank[['RANG', 'REGION', 'Indice', 'Risque']].rename(columns={'RANG':'#','REGION':'Région','Indice':'Indice'}),
        use_container_width=True, hide_index=True, height=380
    )

st.divider()

# ─── LIGNE 2 : EVOLUTION TEMPORELLE DU TAP ──────────────────
st.subheader("📈 Évolution du Taux d'Achèvement au Primaire (TAP) par région")
st.caption("Le TAP mesure la proportion d'élèves qui terminent le primaire. Un TAP en baisse = plus de décrochage.")

df_evol = master[master['REGION'].isin(regions_sel)][['REGION','ANNEE','TAP_total']].dropna()

if not df_evol.empty:
    fig_evol = px.line(
        df_evol, x='ANNEE', y='TAP_total', color='REGION',
        markers=True,
        labels={'TAP_total': 'TAP (%)', 'ANNEE': 'Année scolaire', 'REGION': 'Région'},
        title='Évolution du TAP (2015-16 → 2024-25)'
    )
    fig_evol.add_hline(y=100, line_dash='dash', line_color='gray', opacity=0.4,
                       annotation_text='100% (objectif)')
    fig_evol.add_hrect(y0=0, y1=50, fillcolor='red', opacity=0.05,
                       annotation_text='Zone critique (<50%)', annotation_position='top left')
    fig_evol.update_layout(height=400, xaxis_tickangle=-35,
                           legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig_evol, use_container_width=True)

st.divider()

# ─── LIGNE 3 : TAP + ABANDON PAR RÉGION ─────────────────────
col_bar1, col_bar2 = st.columns(2)

with col_bar1:
    st.subheader(f"📊 TAP par région — {annee_sel}")
    df_bar = df_annee[['REGION','TAP_total']].dropna().sort_values('TAP_total')
    if not df_bar.empty:
        df_bar['couleur'] = df_bar['REGION'].map(
            lambda r: COULEURS_RISQUE.get(
                df_indice[df_indice['REGION']==r]['NIVEAU_RISQUE'].values[0]
                if len(df_indice[df_indice['REGION']==r]) > 0 else 'Inconnu', '#aec7e8')
        )
        fig_bar = px.bar(df_bar, x='TAP_total', y='REGION', orientation='h',
                         color='couleur', color_discrete_map='identity',
                         labels={'TAP_total':'TAP (%)','REGION':'Région'},
                         title=f'Taux d\'achèvement primaire — {annee_sel}')
        fig_bar.add_vline(x=100, line_dash='dash', line_color='gray')
        fig_bar.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

with col_bar2:
    st.subheader(f"⚠️ Taux d'abandon estimé — {annee_sel}")
    df_ab = df_annee[['REGION','TAUX_ABANDON']].dropna().sort_values('TAUX_ABANDON', ascending=False)
    if not df_ab.empty:
        fig_ab = px.bar(df_ab, x='REGION', y='TAUX_ABANDON',
                        color='TAUX_ABANDON',
                        color_continuous_scale=['#2ca02c','#ff7f0e','#d62728'],
                        labels={'TAUX_ABANDON':'Abandon estimé (%)','REGION':'Région'},
                        title=f'Taux d\'abandon estimé (100 - TAP) — {annee_sel}')
        fig_ab.update_layout(height=380, xaxis_tickangle=-45, coloraxis_showscale=False)
        st.plotly_chart(fig_ab, use_container_width=True)

st.divider()

# ─── LIGNE 4 : PARITÉ FILLES/GARÇONS ────────────────────────
st.subheader("⚖️ Parité Filles/Garçons dans l'achèvement (IPS du TAP)")
st.caption("IPS < 1 → les garçons achèvent plus que les filles · IPS > 1 → les filles achèvent plus")

df_ips = master[master['REGION'].isin(regions_sel)][['REGION','ANNEE','IPS_TAP']].dropna()
if not df_ips.empty:
    fig_ips = px.line(df_ips, x='ANNEE', y='IPS_TAP', color='REGION', markers=True,
                      labels={'IPS_TAP':'IPS du TAP','ANNEE':'Année scolaire'},
                      title='Évolution de la parité dans l\'achèvement primaire (IPS TAP)')
    fig_ips.add_hline(y=1.0, line_dash='dash', line_color='black', opacity=0.5,
                      annotation_text='Parité parfaite (1.0)')
    fig_ips.update_layout(height=350, xaxis_tickangle=-35,
                          legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig_ips, use_container_width=True)

st.divider()

# ─── RECOMMANDATIONS ────────────────────────────────────────
st.subheader("💡 Recommandations par région")

regions_risque_eleve = df_indice[df_indice['NIVEAU_RISQUE'] == 'Élevé']['REGION'].tolist()
regions_risque_mod   = df_indice[df_indice['NIVEAU_RISQUE'] == 'Modéré']['REGION'].tolist()

if regions_risque_eleve:
    with st.expander(f"🔴 Régions à risque ÉLEVÉ ({len(regions_risque_eleve)}) — Actions prioritaires", expanded=True):
        for r in regions_risque_eleve:
            row = df_indice[df_indice['REGION'] == r].iloc[0]
            st.markdown(f"**{r}** — Indice : `{row['INDICE_VULNERABILITE']:.3f}` | Rang #{int(row['RANG'])}")
            st.markdown("""
- 🏫 Renforcer l'offre scolaire (infrastructures, enseignants)
- 🎒 Programmes d'aide aux familles (cantine, fournitures)
- 📡 Suivi rapproché des abandons en cours d'année
- 👧 Attention particulière à la scolarisation des filles
""")
            st.divider()

if regions_risque_mod:
    with st.expander(f"🟠 Régions à risque MODÉRÉ ({len(regions_risque_mod)}) — Actions de prévention"):
        for r in regions_risque_mod:
            row = df_indice[df_indice['REGION'] == r].iloc[0]
            st.markdown(f"**{r}** — Indice : `{row['INDICE_VULNERABILITE']:.3f}` | Rang #{int(row['RANG'])}")
            st.markdown("""
- 📊 Surveillance régulière des indicateurs TAP et TBS
- 🤝 Sensibilisation des communautés à la scolarisation
""")
            st.divider()

# ─── DONNÉES BRUTES ─────────────────────────────────────────
with st.expander("📂 Données brutes — Année sélectionnée"):
    cols_affich = [c for c in ['REGION','ANNEE','TAP_total','TBS_total','TBA_total',
                                'TAUX_ABANDON','IPS_TAP','CP1_total','NB_ECOLES'] if c in df_annee.columns]
    st.dataframe(df_annee[cols_affich].set_index('REGION'), use_container_width=True)

# ─── PIED DE PAGE ───────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:gray; font-size:0.85em;'>
EduGuard · Équipe EduData Faso · Data Challenge Burkina 2026 — Édition Éducation<br>
Source : DGESS / Ministère de l'Éducation nationale du Burkina Faso (2016–2025)<br>
<em>« On ne développe pas, on se développe » — l'éthique de l'éducation en Afrique : sur les traces de Joseph Ki-Zerbo</em>
</div>
""", unsafe_allow_html=True)
