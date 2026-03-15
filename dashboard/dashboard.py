import streamlit as st
import pandas as pd
import joblib
import datetime
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="IoT Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── SESSION STATE FOR THEME ──────────────────────────────────────────────────
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'historique_alertes' not in st.session_state:
    st.session_state.historique_alertes = []
if 'derniere_detection' not in st.session_state:
    st.session_state.derniere_detection = None

# ─── GLOBAL CSS (structure only, no colors) ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a1628; }
::-webkit-scrollbar-thumb { background: #1a4a7a; border-radius: 4px; }

.main .block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1400px;
}

h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em;
    margin-bottom: 0.2rem !important;
}
h2, h3 {
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 0.03em;
}
hr {
    border: none;
    margin: 1rem 0;
}

[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

.kpi-card {
    border-radius: 12px;
    padding: 22px 20px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card .kpi-icon { font-size: 1.6rem; margin-bottom: 8px; display: block; }
.kpi-card .kpi-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
    font-weight: 600;
}
.kpi-card .kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.1rem;
    font-weight: 700;
    line-height: 1;
}
.kpi-card .kpi-badge {
    margin-top: 8px;
    font-size: 0.68rem;
    font-family: 'Space Mono', monospace;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.8rem 0 1.1rem;
    padding-bottom: 8px;
}
.section-header .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.section-header span {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 30px;
    font-size: 0.7rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.05em;
}
.badge-haute   { background: rgba(255,60,80,0.18);  color: #ff4d5e; border: 1px solid rgba(255,60,80,0.4); }
.badge-moyenne { background: rgba(255,165,0,0.18);  color: #ffaa33; border: 1px solid rgba(255,165,0,0.4); }
.badge-basse   { background: rgba(0,230,130,0.18);  color: #00e682; border: 1px solid rgba(0,230,130,0.4); }

.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 30px;
    padding: 4px 12px;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.08em;
}
.live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.15; }
}

.stPlotlyChart > div { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.streamlit-expanderHeader {
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}
.stCaption { font-size: 0.72rem !important; }
.stAlert   { border-radius: 10px !important; }

.footer-text {
    text-align: center;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.08em;
    margin-top: 2rem;
    padding-top: 1rem;
}
.model-best { color: #00e682 !important; }
</style>
""", unsafe_allow_html=True)

# ─── DYNAMIC THEME CSS ────────────────────────────────────────────────────────
def inject_theme(dark: bool):
    if dark:
        st.markdown("""
        <style>
        html, body, [class*="css"],
        .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"] {
            background-color: #050d1a !important;
            color: #c8d8e8 !important;
        }
        .main, .main .block-container { background-color: #050d1a !important; }
        section[data-testid="stSidebar"] > div:first-child { background-color: #040c18 !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#040c18 0%,#071525 60%,#040c18 100%) !important; border-right: 1px solid rgba(0,180,255,0.15); }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown { color: #7ec8f0 !important; }
        h1 { color: #e8f4ff !important; text-shadow: 0 0 28px rgba(0,180,255,0.45); }
        h2, h3 { color: #7ec8f0 !important; }
        hr { border-top: 1px solid rgba(0,180,255,0.18); }
        .kpi-card { background: linear-gradient(135deg,#071a30 0%,#0a2040 100%); border: 1px solid rgba(0,180,255,0.22); box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .kpi-card:hover { box-shadow: 0 8px 32px rgba(0,180,255,0.18); }
        .kpi-card::before { background: linear-gradient(90deg,transparent,#00b4ff,transparent); }
        .kpi-card .kpi-label { color: #5a8aaa; }
        .kpi-card .kpi-value { color: #e8f4ff; text-shadow: 0 0 20px rgba(0,180,255,0.4); }
        .kpi-card .kpi-badge { color: #00b4ff; }
        .section-header { border-bottom: 1px solid rgba(0,180,255,0.14); }
        .section-header .dot { background: #00b4ff; box-shadow: 0 0 10px #00b4ff; }
        .section-header span { color: #7ec8f0; }
        .live-pill { background: rgba(0,230,130,0.1); border: 1px solid rgba(0,230,130,0.35); color: #00e682; }
        .live-dot { background: #00e682; }
        .stPlotlyChart > div { border: 1px solid rgba(0,180,255,0.12); }
        [data-testid="stDataFrame"] { border: 1px solid rgba(0,180,255,0.14); }
        .streamlit-expanderHeader { background: rgba(0,180,255,0.07) !important; border: 1px solid rgba(0,180,255,0.18) !important; color: #7ec8f0 !important; }
        .stCaption { color: #4a7a9a !important; }
        .footer-text { color: #2a4a6a; border-top: 1px solid rgba(0,180,255,0.08); }
        .main::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,180,255,0.013) 2px,rgba(0,180,255,0.013) 4px);
            pointer-events: none;
            z-index: 9999;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        html, body, [class*="css"],
        .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"] {
            background-color: #f0f4f8 !important;
            color: #1a2b3c !important;
        }
        .main, .main .block-container { background-color: #f0f4f8 !important; }
        section[data-testid="stSidebar"] > div:first-child { background-color: #0d2a4a !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#0d2a4a 0%,#163a60 60%,#0d2a4a 100%) !important; border-right: 1px solid rgba(0,100,200,0.2); }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown { color: #aaccee !important; }
        h1 { color: #0d2a4a !important; text-shadow: none !important; }
        h2, h3 { color: #1a4a7a !important; }
        hr { border-top: 1px solid rgba(0,100,200,0.18); }
        .kpi-card { background: linear-gradient(135deg,#ffffff 0%,#e8f0f8 100%); border: 1px solid rgba(0,100,200,0.25); box-shadow: 0 4px 16px rgba(0,50,120,0.08); }
        .kpi-card:hover { box-shadow: 0 8px 28px rgba(0,100,200,0.15); }
        .kpi-card::before { background: linear-gradient(90deg,transparent,#1a6bbf,transparent); }
        .kpi-card .kpi-label { color: #5a7a9a; }
        .kpi-card .kpi-value { color: #0d2a4a; text-shadow: none; }
        .kpi-card .kpi-badge { color: #1a6bbf; }
        .section-header { border-bottom: 1px solid rgba(0,100,200,0.18); }
        .section-header .dot { background: #1a6bbf; box-shadow: 0 0 10px rgba(26,107,191,0.5); }
        .section-header span { color: #1a4a7a; }
        .live-pill { background: rgba(0,150,100,0.1); border: 1px solid rgba(0,150,100,0.35); color: #007a50; }
        .live-dot { background: #007a50; }
        .stPlotlyChart > div { border: 1px solid rgba(0,100,200,0.15); }
        [data-testid="stDataFrame"] { border: 1px solid rgba(0,100,200,0.18); }
        .streamlit-expanderHeader { background: rgba(0,100,200,0.07) !important; border: 1px solid rgba(0,100,200,0.18) !important; color: #1a4a7a !important; }
        .stCaption { color: #5a7a9a !important; }
        .footer-text { color: #7a9aaa; border-top: 1px solid rgba(0,100,200,0.12); }
        .main::before { display: none; }
        </style>
        """, unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(7, 20, 38, 0.7)',
    font=dict(family='DM Sans, sans-serif', color='#8aaabf', size=12),
    title_font=dict(family='Space Mono, monospace', color='#c8d8e8', size=13),
    xaxis=dict(gridcolor='rgba(0,180,255,0.07)', linecolor='rgba(0,180,255,0.2)', tickcolor='rgba(0,180,255,0.2)'),
    yaxis=dict(gridcolor='rgba(0,180,255,0.07)', linecolor='rgba(0,180,255,0.2)', tickcolor='rgba(0,180,255,0.2)'),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,180,255,0.15)', borderwidth=1),
)
ACCENT_COLORS = ['#00b4ff', '#00e682', '#ff4d5e', '#ffaa33', '#a855f7', '#ff6b35']

# ─── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_data():
    dataset = pd.read_csv("dataset_iot_prepare.csv", engine='python')
    model   = joblib.load("modele_logistic_regression.pkl")
    scaler  = joblib.load("scaler.pkl")
    return dataset, model, scaler

dataset, model, scaler = load_data()

# ─── FONCTION POUR LIRE LES DÉTECTIONS EN TEMPS RÉEL ────────────────────────
def lire_detection():
    """Lit le fichier JSON contenant la dernière détection."""
    chemin_fichier = "detection_realtime.json"  # Pour Linux/Mac
    # Pour Windows, utiliser plutôt : chemin_fichier = "C:/temp/detection_realtime.json"
    try:
        with open(chemin_fichier, 'r') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 8px 0 20px;">
        <div style="font-size:2.4rem; margin-bottom:6px;">🛡️</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.72rem;
                    letter-spacing:0.18em; color:#00b4ff; text-transform:uppercase;">
            IoT · SecOps
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:0.6rem;
                    letter-spacing:0.12em; color:#2a5a7a; margin-top:2px;">
            v2.1.0 — Hôpital
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = option_menu(
        menu_title=None,
        options=["Accueil", "Modèles", "Alertes"],
        icons=["house-fill", "cpu-fill", "bell-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container":        {"padding": "4px 0", "background-color": "transparent"},
            "icon":             {"color": "#00b4ff", "font-size": "15px"},
            "nav-link":         {
                "font-family":  "Space Mono, monospace",
                "font-size":    "0.76rem",
                "letter-spacing": "0.08em",
                "text-transform": "uppercase",
                "color":        "#7ec8f0",
                "padding":      "10px 14px",
                "border-radius": "8px",
                "--hover-color": "rgba(0,180,255,0.12)",
            },
            "nav-link-selected": {
                "background-color": "rgba(0,180,255,0.15)",
                "color":           "#e8f4ff",
                "border-left":     "3px solid #00b4ff",
            },
        }
    )

    st.markdown("<hr style='margin:16px 0; border-color:rgba(0,180,255,0.12);'>", unsafe_allow_html=True)

    # Live status
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div style="padding:10px 8px;">
        <div class="live-pill">
            <div class="live-dot"></div> SYSTÈME ACTIF — {now}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:16px; padding:12px; background:rgba(0,180,255,0.06);
                border:1px solid rgba(0,180,255,0.14); border-radius:10px;
                font-size:0.7rem; color:#5a8aaa; line-height:1.6;">
        Ce dashboard surveille le trafic réseau IoT en milieu hospitalier et détecte
        les intrusions en temps réel via des modèles TinyML embarqués.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.session_state.dark_mode = st.toggle("🌙 Mode sombre", value=st.session_state.dark_mode)

# ─── APPLY THEME ──────────────────────────────────────────────────────────────
inject_theme(st.session_state.dark_mode)

# Update plotly layout based on theme
if st.session_state.dark_mode:
    PLOTLY_BG       = 'rgba(0,0,0,0)'
    PLOTLY_PLOT_BG  = 'rgba(7, 20, 38, 0.7)'
    PLOTLY_FONT_CLR = '#8aaabf'
    PLOTLY_TITLE_CLR= '#c8d8e8'
    PLOTLY_GRID_CLR = 'rgba(0,180,255,0.07)'
    PLOTLY_LINE_CLR = 'rgba(0,180,255,0.2)'
else:
    PLOTLY_BG       = 'rgba(0,0,0,0)'
    PLOTLY_PLOT_BG  = 'rgba(230,240,250,0.85)'
    PLOTLY_FONT_CLR = '#3a5a7a'
    PLOTLY_TITLE_CLR= '#0d2a4a'
    PLOTLY_GRID_CLR = 'rgba(0,100,200,0.1)'
    PLOTLY_LINE_CLR = 'rgba(0,100,200,0.25)'

PLOTLY_LAYOUT['paper_bgcolor'] = PLOTLY_BG
PLOTLY_LAYOUT['plot_bgcolor']  = PLOTLY_PLOT_BG
PLOTLY_LAYOUT['font']          = dict(family='DM Sans, sans-serif', color=PLOTLY_FONT_CLR, size=12)
PLOTLY_LAYOUT['title_font']    = dict(family='Space Mono, monospace', color=PLOTLY_TITLE_CLR, size=13)
PLOTLY_LAYOUT['xaxis']         = dict(gridcolor=PLOTLY_GRID_CLR, linecolor=PLOTLY_LINE_CLR, tickcolor=PLOTLY_LINE_CLR)
PLOTLY_LAYOUT['yaxis']         = dict(gridcolor=PLOTLY_GRID_CLR, linecolor=PLOTLY_LINE_CLR, tickcolor=PLOTLY_LINE_CLR)

# ─── PAGE: ACCUEIL ────────────────────────────────────────────────────────────
if page == "Accueil":
    # Header
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.title("🛡️  IoT Security Dashboard")
        st.markdown(
            "<p style='color:#4a7a9a; font-size:0.85rem; margin-top:-4px;'>"
            "Détection d'intrusions en milieu hospitalier — Supervision en temps réel"
            "</p>", unsafe_allow_html=True
        )
    with col_status:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        total_lignes = len(dataset)
        total_attaques = dataset['Label'].sum()
        total_normaux = total_lignes - total_attaques
        taux_attaque = (total_attaques / total_lignes) * 100
        threat_level = "CRITIQUE" if taux_attaque > 30 else ("MODÉRÉ" if taux_attaque > 10 else "FAIBLE")
        threat_color = "#ff4d5e" if taux_attaque > 30 else ("#ffaa33" if taux_attaque > 10 else "#00e682")
        st.markdown(f"""
        <div style="background:rgba({('255,77,94' if taux_attaque > 30 else ('255,170,51' if taux_attaque > 10 else '0,230,130'))},0.1);
                    border:1px solid {threat_color}44; border-radius:10px;
                    padding:12px 16px; text-align:right;">
            <div style="font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase;
                        color:#5a8aaa; font-family:'Space Mono',monospace;">Niveau de menace</div>
            <div style="font-family:'Space Mono',monospace; font-size:1.1rem;
                        font-weight:700; color:{threat_color}; margin-top:2px;">{threat_level}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("c1", "📦", "TOTAL ÉCHANTILLONS", f"{total_lignes:,}", "Dataset chargé"),
        ("c2", "✅", "TRAFIC NORMAL",       f"{total_normaux:,}", f"{100-taux_attaque:.1f}% du trafic"),
        ("c3", "⚠️",  "ATTAQUES DÉTECTÉES", f"{total_attaques:,}", f"{taux_attaque:.1f}% du trafic"),
        ("c4", "📡",  "TAUX D'ATTAQUE",     f"{taux_attaque:.2f}%", "Indice global de risque"),
    ]
    for col, (key, icon, label, value, badge) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <span class="kpi-icon">{icon}</span>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-badge">↗ {badge}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Charts
    st.markdown("""
    <div class="section-header">
        <div class="dot"></div>
        <span>Répartition du trafic</span>
    </div>
    """, unsafe_allow_html=True)

    attack_counts = dataset['Attack_Type'].value_counts().reset_index()
    attack_counts.columns = ['Type', 'Nombre']

    col_bar, col_pie = st.columns([3, 2])
    with col_bar:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=attack_counts['Type'],
            y=attack_counts['Nombre'],
            marker=dict(
                color=attack_counts['Nombre'],
                colorscale=[[0, '#0a2a4a'], [0.5, '#0070b8'], [1, '#00b4ff']],
                line=dict(color='rgba(0,180,255,0.3)', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Échantillons: %{y:,}<extra></extra>'
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Nombre d'échantillons par type de trafic",
            bargap=0.3,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=attack_counts['Type'],
            values=attack_counts['Nombre'],
            hole=0.55,
            marker=dict(
                colors=ACCENT_COLORS,
                line=dict(color='#050d1a', width=2)
            ),
            hovertemplate='<b>%{label}</b><br>%{value:,} échantillons<br>%{percent}<extra></extra>',
            textfont=dict(family='Space Mono, monospace', size=10),
        ))
        pie_layout = {**PLOTLY_LAYOUT, 'legend': dict(font=dict(size=10), orientation='v')}
        fig_pie.update_layout(
            **pie_layout,
            title="Distribution proportionnelle",
            showlegend=True,
            annotations=[dict(
                text=f"<b>{total_lignes:,}</b><br><span style='font-size:10'>total</span>",
                x=0.5, y=0.5, font=dict(size=13, color='#c8d8e8', family='Space Mono'),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Aperçu données
    st.markdown("""
    <div class="section-header">
        <div class="dot"></div>
        <span>Aperçu des données brutes</span>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("🔍  Afficher les 10 premières lignes du dataset"):
        st.dataframe(
            dataset.head(10).style.set_properties(**{
                'background-color': '#071a30',
                'color': '#c8d8e8',
                'border-color': 'rgba(0,180,255,0.15)'
            }),
            use_container_width=True
        )

# ─── PAGE: MODÈLES ────────────────────────────────────────────────────────────
elif page == "Modèles":
    st.title("⚙️  Comparaison des modèles TinyML")
    st.markdown(
        "<p style='color:#4a7a9a; font-size:0.85rem; margin-top:-4px;'>"
        "Évaluation des performances et de l'efficacité énergétique</p>",
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    # NOUVELLES DONNÉES fournies par le collègue
    data = {
        "Modèle": [
            "Seuil Simple (baseline)",
            "Régression Logistique (base)",
            "Arbre de Décision (base)",
            "Arbre Optimisé",
            "Régression Pondérée",
            "Random Forest Léger",
            "Voting Classifier"
        ],
        "Accuracy": [
            0.7727,   # Seuil Simple
            0.8168,   # Régression Logistique
            0.8550,   # Arbre de base
            0.8817,   # Arbre Optimisé (MEILLEUR)
            0.7622,   # Régression Pondérée
            0.8332,   # Random Forest
            0.8808    # Voting Classifier
        ],
        "Énergie (J)": [
            0.7246,   # Seuil Simple (100 éch.)
            0.0407,   # Régression Logistique
            0.0790,   # Arbre de Décision
            0.0790,   # Arbre Optimisé (même énergie)
            0.0407,   # Régression Pondérée
            0.0790,   # Random Forest
            0.0790    # Voting Classifier
        ]
    }
    df_models = pd.DataFrame(data)

    # Tableau comparatif
    st.markdown("""
    <div class="section-header">
        <div class="dot"></div>
        <span>Tableau comparatif</span>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(
        df_models.style
            .highlight_max(axis=0, subset=['Accuracy'], color='#0d3a1a')
            .highlight_min(axis=0, subset=['Énergie (J)'], color='#0d1f3a')
            .set_properties(**{'background-color': '#071a30', 'color': '#c8d8e8', 'border-color': 'rgba(0,180,255,0.15)'}),
        use_container_width=True
    )

    # Graphiques côte à côte (Accuracy et Énergie)
    st.markdown("""
    <div class="section-header" style="margin-top:1.8rem">
        <div class="dot"></div>
        <span>Visualisation des performances</span>
    </div>
    """, unsafe_allow_html=True)

    col_acc, col_energy = st.columns(2)

    with col_acc:
        fig_acc = px.bar(
            df_models,
            x='Modèle',
            y='Accuracy',
            color='Modèle',
            title="Accuracy des modèles",
            color_discrete_sequence=ACCENT_COLORS
        )
        fig_acc.update_layout(showlegend=False, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_acc, use_container_width=True)

    with col_energy:
        fig_energy = px.bar(
            df_models,
            x='Modèle',
            y='Énergie (J)',
            color='Modèle',
            title="Consommation énergétique (Joules)",
            color_discrete_sequence=ACCENT_COLORS
        )
        fig_energy.update_layout(showlegend=False, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_energy, use_container_width=True)

    # Matrice de confusion (simulée pour l'exemple)
    st.markdown("""
    <div class="section-header">
        <div class="dot"></div>
        <span>Matrice de confusion — Régression Logistique</span>
    </div>
    """, unsafe_allow_html=True)

    import numpy as np
    cm = np.array([[2970, 30], [25, 975]])
    fig_cm = go.Figure(go.Heatmap(
        z=cm,
        x=['Prédit Normal', 'Prédit Attaque'],
        y=['Réel Normal', 'Réel Attaque'],
        colorscale=[[0, '#040c18'], [0.5, '#0a3060'], [1, '#00b4ff']],
        text=cm, texttemplate='<b>%{text}</b>',
        textfont=dict(family='Space Mono, monospace', size=20, color='#e8f4ff'),
        hovertemplate='%{y} → %{x}<br>Nombre: %{z}<extra></extra>',
        showscale=False,
    ))
    cm_layout = {**PLOTLY_LAYOUT}
    cm_layout['xaxis'] = dict(side='bottom', **PLOTLY_LAYOUT['xaxis'])
    fig_cm.update_layout(
        **cm_layout,
        title="Matrice de confusion",
    )
    st.plotly_chart(fig_cm, use_container_width=True)

# ─── PAGE: ALERTES (TEMPS RÉEL) ─────────────────────────────────────────────
elif page == "Alertes":
    st.title("🚨  Alertes de sécurité en temps réel")
    st.markdown(
        "<p style='color:#4a7a9a; font-size:0.85rem; margin-top:-4px;'>"
        "Dernières détections issues du module d'intrusion</p>",
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    # Lire la dernière détection
    detection = lire_detection()

    # Si nouvelle détection et différente de la précédente, l'ajouter à l'historique
    if detection and detection != st.session_state.derniere_detection:
        st.session_state.historique_alertes.insert(0, detection)
        st.session_state.derniere_detection = detection
        # Garder seulement les 100 dernières
        if len(st.session_state.historique_alertes) > 100:
            st.session_state.historique_alertes = st.session_state.historique_alertes[:100]

    # Afficher l'historique
    if st.session_state.historique_alertes:
        # Convertir en DataFrame
        df_alertes = pd.DataFrame(st.session_state.historique_alertes)
        # Transformer le timestamp en datetime
        df_alertes['Horodatage'] = pd.to_datetime(df_alertes['timestamp'])
        # Ajouter une colonne Sévérité basée sur 'est_attaque' (on peut affiner avec confiance)
        df_alertes['Sévérité'] = df_alertes['est_attaque'].apply(
            lambda x: 'Haute' if x else 'Basse'
        )
        # Renommer les colonnes pour l'affichage
        df_alertes.rename(columns={
            'type': 'Type',
            'confiance': 'Confiance (%)'
        }, inplace=True)
        df_alertes = df_alertes[['Horodatage', 'Type', 'Confiance (%)', 'Sévérité']]

        # Afficher le tableau avec mise en forme
        def color_severity(val):
            if val == 'Haute':
                return 'background-color:#2a0a0a; color:#ff4d5e; font-weight:bold'
            else:
                return 'background-color:#001a0a; color:#00e682; font-weight:bold'

        st.dataframe(
            df_alertes.style
                .applymap(color_severity, subset=['Sévérité'])
                .set_properties(**{'background-color': '#071a30', 'color': '#c8d8e8', 'border-color': 'rgba(0,180,255,0.1)'}),
            use_container_width=True
        )
        st.caption("🔴 Attaque détectée   🟢 Trafic normal")
    else:
        st.info("Aucune détection pour l'instant. En attente de données...")

    # Bouton pour rafraîchir manuellement (optionnel)
    if st.button("🔄 Rafraîchir"):
        st.rerun()

    # Optionnel : rafraîchissement automatique toutes les 5 secondes
    # (décommente si tu veux)
    # st.markdown("""<meta http-equiv="refresh" content="5">""", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='footer-text'>DASHBOARD IOT SECURITÉ — PROJET 2025 — DÉVELOPPÉ AVEC STREAMLIT</div>",
    unsafe_allow_html=True
)