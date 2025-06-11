import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from PIL import Image
import io

# Configuration de la page
st.set_page_config(
    page_title="FoodSafe AI - Sécurité Alimentaire",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4ECDC4;
    }
    .risk-high { border-left-color: #FF6B6B !important; }
    .risk-medium { border-left-color: #FFE66D !important; }
    .risk-low { border-left-color: #4ECDC4 !important; }
    .alert-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .alert-danger { background-color: #ffe6e6; border-left: 4px solid #FF6B6B; }
    .alert-warning { background-color: #fff3cd; border-left: 4px solid #FFE66D; }
    .alert-success { background-color: #d4edda; border-left: 4px solid #4ECDC4; }
</style>
""", unsafe_allow_html=True)

# Données simulées pour l'exemple
@st.cache_data
def load_sample_data():
    # Base de données des produits avec risques
    products_db = {
        "Lait entier Carrefour": {"risk": "low", "dlu": "2024-06-15", "lot": "L240601", "recalls": 0},
        "Yaourt Danone": {"risk": "low", "dlu": "2024-06-20", "lot": "Y240605", "recalls": 0},
        "Fromage Roquefort AOP": {"risk": "medium", "dlu": "2024-07-01", "lot": "R240520", "recalls": 1},
        "Salade Caesar prête": {"risk": "high", "dlu": "2024-06-12", "lot": "S240610", "recalls": 3},
        "Saumon fumé Label Rouge": {"risk": "medium", "dlu": "2024-06-18", "lot": "SF240608", "recalls": 1},
        "Chocolat noir Lindt": {"risk": "low", "dlu": "2024-12-01", "lot": "C240301", "recalls": 0},
        "Épinards surgelés": {"risk": "high", "dlu": "2024-08-15", "lot": "E240515", "recalls": 2}
    }
    
    # Données des rappels récents
    recalls_data = [
        {"date": "2024-06-10", "product": "Salade Caesar prête", "reason": "Listeria monocytogenes", "severity": "Élevé"},
        {"date": "2024-06-08", "product": "Épinards surgelés", "reason": "Pesticides non conformes", "severity": "Moyen"},
        {"date": "2024-06-05", "product": "Fromage Roquefort AOP", "reason": "E. coli", "severity": "Élevé"},
        {"date": "2024-06-03", "product": "Saumon fumé Label Rouge", "reason": "Température non respectée", "severity": "Moyen"},
    ]
    
    return products_db, recalls_data

def analyze_food_risk(product_name, lot_number=None, expiry_date=None):
    """Analyse le risque d'un produit alimentaire"""
    products_db, _ = load_sample_data()
    
    if product_name in products_db:
        product_info = products_db[product_name]
        risk_level = product_info["risk"]
        recalls_count = product_info["recalls"]
        
        # Calcul du score de risque
        base_score = {"low": 20, "medium": 60, "high": 85}[risk_level]
        recall_penalty = recalls_count * 15
        
        # Vérification de la date de péremption
        expiry_penalty = 0
        if expiry_date:
            try:
                exp_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                days_to_expiry = (exp_date - datetime.now()).days
                if days_to_expiry < 0:
                    expiry_penalty = 50
                elif days_to_expiry < 3:
                    expiry_penalty = 30
                elif days_to_expiry < 7:
                    expiry_penalty = 15
            except:
                pass
        
        final_score = min(100, base_score + recall_penalty + expiry_penalty)
        
        return {
            "risk_score": final_score,
            "risk_level": "Élevé" if final_score > 70 else "Moyen" if final_score > 40 else "Faible",
            "recalls_count": recalls_count,
            "recommendations": get_recommendations(final_score, days_to_expiry if 'days_to_expiry' in locals() else None),
            "lot_info": product_info.get("lot", "Non disponible")
        }
    else:
        # Analyse générique pour les produits non référencés
        generic_score = random.randint(15, 45)
        return {
            "risk_score": generic_score,
            "risk_level": "Faible",
            "recalls_count": 0,
            "recommendations": ["Produit non référencé dans notre base de données", "Vérifiez les dates de péremption", "Conservez dans de bonnes conditions"],
            "lot_info": lot_number or "Non spécifié"
        }

def get_recommendations(risk_score, days_to_expiry):
    """Génère des recommandations basées sur le score de risque"""
    recommendations = []
    
    if risk_score > 70:
        recommendations.extend([
            "⚠️ ATTENTION: Risque élevé détecté",
            "Ne consommez pas ce produit",
            "Vérifiez les rappels officiels sur le site de la DGCCRF"
        ])
    elif risk_score > 40:
        recommendations.extend([
            "⚡ Risque modéré identifié",
            "Vérifiez l'aspect et l'odeur avant consommation",
            "Respectez scrupuleusement les conditions de conservation"
        ])
    else:
        recommendations.extend([
            "✅ Produit considéré comme sûr",
            "Respectez les dates de péremption",
            "Conservez selon les instructions"
        ])
    
    if days_to_expiry is not None:
        if days_to_expiry < 0:
            recommendations.append("🚨 PRODUIT PÉRIMÉ - Ne pas consommer")
        elif days_to_expiry < 3:
            recommendations.append("⏰ Consommer rapidement (expire dans moins de 3 jours)")
    
    return recommendations

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🍎 FoodSafe AI</h1>
        <h3>Intelligence Artificielle pour la Sécurité Alimentaire</h3>
        <p>Vérifiez la sécurité de vos produits alimentaires en temps réel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour la navigation
    st.sidebar.title("🔍 Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une fonctionnalité",
        ["Analyser un produit", "Tableau de bord des rappels", "Alertes personnalisées", "Statistiques globales"]
    )
    
    if page == "Analyser un produit":
        analyze_product_page()
    elif page == "Tableau de bord des rappels":
        recalls_dashboard()
    elif page == "Alertes personnalisées":
        alerts_page()
    else:
        statistics_page()

def analyze_product_page():
    st.header("🔍 Analyse de Produit Alimentaire")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Informations du produit")
        
        # Méthodes d'entrée
        input_method = st.radio(
            "Comment souhaitez-vous identifier le produit ?",
            ["Nom du produit", "Code-barres", "Photo du produit"]
        )
        
        if input_method == "Nom du produit":
            product_name = st.text_input(
                "Nom du produit",
                placeholder="Ex: Lait entier Carrefour",
                help="Tapez le nom exact du produit tel qu'il apparaît sur l'emballage"
            )
        elif input_method == "Code-barres":
            barcode = st.text_input(
                "Code-barres (EAN-13)",
                placeholder="Ex: 3245412345678",
                help="Scannez ou tapez le code-barres du produit"
            )
            # Simulation de recherche par code-barres
            if barcode and len(barcode) == 13:
                product_name = "Produit identifié par code-barres"
            else:
                product_name = None
        else:
            uploaded_file = st.file_uploader(
                "Téléchargez une photo du produit",
                type=["jpg", "jpeg", "png"],
                help="Prenez une photo claire de l'étiquette du produit"
            )
            if uploaded_file:
                st.image(uploaded_file, caption="Photo du produit", width=300)
                product_name = "Produit identifié par photo"
            else:
                product_name = None
        
        # Informations complémentaires
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            lot_number = st.text_input("Numéro de lot (optionnel)", placeholder="Ex: L240601")
        with col_info2:
            expiry_date = st.date_input("Date de péremption (optionnel)")
        
        # Bouton d'analyse
        if st.button("🔍 Analyser le produit", type="primary"):
            if product_name:
                with st.spinner("Analyse en cours..."):
                    # Simulation d'un délai d'analyse
                    import time
                    time.sleep(2)
                    
                    expiry_str = expiry_date.strftime("%Y-%m-%d") if expiry_date else None
                    analysis = analyze_food_risk(product_name, lot_number, expiry_str)
                    
                    # Affichage des résultats
                    display_analysis_results(analysis, product_name)
            else:
                st.warning("Veuillez identifier un produit avant de lancer l'analyse.")
    
    with col2:
        st.subheader("💡 Conseils")
        st.info("""
        **Comment obtenir la meilleure analyse ?**
        
        1. **Nom exact**: Utilisez le nom complet du produit
        2. **Numéro de lot**: Trouvez-le sur l'emballage (commence souvent par L ou LOT)
        3. **Date**: Vérifiez la DLC/DLUO sur l'emballage
        4. **Photo**: Assurez-vous que l'étiquette est lisible
        """)
        
        st.warning("""
        **⚠️ Avertissement**
        
        Cette application est un outil d'aide à la décision. En cas de doute, consultez les sources officielles (DGCCRF, Rappel Conso).
        """)

def display_analysis_results(analysis, product_name):
    """Affiche les résultats de l'analyse"""
    st.subheader("📊 Résultats de l'analyse")
    
    # Score de risque principal
    risk_score = analysis["risk_score"]
    risk_level = analysis["risk_level"]
    
    # Couleur selon le niveau de risque
    if risk_level == "Élevé":
        color = "#FF6B6B"
        alert_class = "alert-danger"
    elif risk_level == "Moyen":
        color = "#FFE66D"
        alert_class = "alert-warning"
    else:
        color = "#4ECDC4"
        alert_class = "alert-success"
    
    # Affichage du score principal
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Score de Risque",
            value=f"{risk_score}/100",
            delta=f"Niveau {risk_level}",
            delta_color="inverse" if risk_level == "Élevé" else "normal"
        )
    
    with col2:
        st.metric(
            label="Rappels enregistrés",
            value=analysis["recalls_count"],
            delta="derniers 6 mois"
        )
    
    with col3:
        st.metric(
            label="Lot analysé",
            value=analysis["lot_info"][:10] + "..." if len(analysis["lot_info"]) > 10 else analysis["lot_info"]
        )
    
    with col4:
        confidence = 85 + random.randint(-10, 10)
        st.metric(
            label="Fiabilité",
            value=f"{confidence}%",
            delta="IA + Base données"
        )
    
    # Graphique du score de risque
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Niveau de Risque: {risk_level}"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations
    st.markdown(f"""
    <div class="alert-box {alert_class}">
        <h4>🎯 Recommandations pour "{product_name}"</h4>
    </div>
    """, unsafe_allow_html=True)
    
    for i, rec in enumerate(analysis["recommendations"], 1):
        st.write(f"{i}. {rec}")
    
    # Actions suggérées
    st.subheader("🚀 Actions suggérées")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📱 Créer une alerte"):
            st.success("Alerte créée ! Vous serez notifié en cas de rappel.")
    
    with col2:
        if st.button("📤 Signaler un problème"):
            st.info("Formulaire de signalement ouvert.")
    
    with col3:
        if st.button("📋 Télécharger le rapport"):
            st.success("Rapport PDF généré !")

def recalls_dashboard():
    st.header("🚨 Tableau de Bord des Rappels")
    
    # Chargement des données de rappels
    _, recalls_data = load_sample_data()
    recalls_df = pd.DataFrame(recalls_data)
    recalls_df['date'] = pd.to_datetime(recalls_df['date'])
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Rappels cette semaine",
            len(recalls_df[recalls_df['date'] >= datetime.now() - timedelta(days=7)]),
            delta="+2 vs semaine précédente"
        )
    
    with col2:
        high_severity = len(recalls_df[recalls_df['severity'] == 'Élevé'])
        st.metric("Sévérité élevée", high_severity, delta=f"{high_severity}/4 total")
    
    with col3:
        st.metric("Catégories affectées", 4, delta="Frais, Surgelés, Conserves")
    
    with col4:
        st.metric("Taux de résolution", "89%", delta="+5% ce mois")
    
    # Graphique des rappels par date
    st.subheader("📈 Évolution des rappels")
    
    fig = px.line(
        recalls_df.sort_values('date'), 
        x='date', 
        y=[1]*len(recalls_df),
        title="Rappels par jour",
        markers=True
    )
    fig.update_traces(y=recalls_df.index + 1)
    fig.update_layout(showlegend=False, yaxis_title="Nombre cumulé de rappels")
    st.plotly_chart(fig, use_container_width=True)
    
    # Liste des rappels récents
    st.subheader("📋 Rappels récents")
    
    for _, recall in recalls_df.iterrows():
        severity_color = "#FF6B6B" if recall['severity'] == 'Élevé' else "#FFE66D"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {severity_color} !important;">
            <h5>{recall['product']}</h5>
            <p><strong>Date:</strong> {recall['date'].strftime('%d/%m/%Y')}</p>
            <p><strong>Motif:</strong> {recall['reason']}</p>
            <p><strong>Sévérité:</strong> <span style="color: {severity_color}; font-weight: bold;">{recall['severity']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

def alerts_page():
    st.header("🔔 Alertes Personnalisées")
    
    st.write("Configurez vos alertes pour être notifié en temps réel des rappels qui vous concernent.")
    
    # Configuration des alertes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Préférences d'alerte")
        
        # Types de produits
        product_types = st.multiselect(
            "Types de produits à surveiller",
            ["Produits laitiers", "Viandes", "Poissons", "Légumes", "Fruits", "Conserves", "Surgelés", "Boulangerie"],
            default=["Produits laitiers", "Viandes"]
        )
        
        # Marques préférées
        brands = st.text_area(
            "Marques préférées (une par ligne)",
            placeholder="Carrefour\nDanone\nNestlé",
            help="Ajoutez les marques que vous achetez régulièrement"
        )
        
        # Niveau de sévérité minimum
        min_severity = st.selectbox(
            "Niveau de sévérité minimum",
            ["Tous", "Moyen", "Élevé"],
            index=1
        )
        
        # Canal de notification
        notification_channel = st.selectbox(
            "Canal de notification",
            ["Email", "SMS", "Push notification", "Tous"]
        )
        
        if st.button("💾 Sauvegarder les préférences"):
            st.success("Préférences sauvegardées ! Vous recevrez des alertes selon vos critères.")
    
    with col2:
        st.subheader("📊 Statistiques de vos alertes")
        
        # Données simulées
        alert_stats = {
            "Alertes envoyées ce mois": 12,
            "Alertes critiques": 3,
            "Produits surveillés": len(product_types) if product_types else 0,
            "Marques surveillées": len(brands.split('\n')) if brands else 0
        }
        
        for stat_name, stat_value in alert_stats.items():
            st.metric(stat_name, stat_value)
        
        st.subheader("🎯 Dernières alertes")
        
        sample_alerts = [
            {"date": "11/06/2024", "product": "Salade Caesar", "severity": "Élevé"},
            {"date": "09/06/2024", "product": "Yaourt Danone", "severity": "Moyen"},
            {"date": "07/06/2024", "product": "Saumon fumé", "severity": "Élevé"},
        ]
        
        for alert in sample_alerts:
            severity_color = "#FF6B6B" if alert['severity'] == 'Élevé' else "#FFE66D"
            st.markdown(f"""
            <div style="padding: 0.5rem; border-left: 3px solid {severity_color}; margin: 0.5rem 0; background: #f8f9fa;">
                <strong>{alert['product']}</strong><br>
                <small>{alert['date']} - {alert['severity']}</small>
            </div>
            """, unsafe_allow_html=True)

def statistics_page():
    st.header("📊 Statistiques Globales de Sécurité Alimentaire")
    
    # Données simulées pour les statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Produits analysés", "2,847,392", delta="+15% ce mois")
    with col2:
        st.metric("Rappels évités", "1,247", delta="Grâce aux alertes précoces")
    with col3:
        st.metric("Utilisateurs protégés", "89,432", delta="+342 cette semaine")
    
    # Graphiques de tendances
    st.subheader("📈 Tendances de sécurité alimentaire")
    
    # Données simulées pour les graphiques
    dates = pd.date_range(start='2024-01-01', end='2024-06-11', freq='D')
    risk_data = np.random.normal(45, 15, len(dates))
    risk_data = np.clip(risk_data, 0, 100)
    
    trend_df = pd.DataFrame({
        'Date': dates,
        'Score_Risque_Moyen': risk_data,
        'Rappels': np.random.poisson(0.3, len(dates)),
        'Analyses': np.random.normal(1000, 200, len(dates))
    })
    
    # Graphique du score de risque moyen
    fig1 = px.line(trend_df, x='Date', y='Score_Risque_Moyen', 
                   title="Évolution du score de risque moyen",
                   color_discrete_sequence=['#FF6B6B'])
    fig1.add_hline(y=50, line_dash="dash", line_color="gray", 
                   annotation_text="Seuil d'alerte")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Répartition des risques par catégorie
    col1, col2 = st.columns(2)
    
    with col1:
        categories = ['Produits laitiers', 'Viandes', 'Légumes', 'Poissons', 'Conserves']
        risk_counts = [23, 45, 12, 34, 18]
        
        fig2 = px.pie(values=risk_counts, names=categories, 
                      title="Répartition des alertes par catégorie",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        severity_data = {'Faible': 156, 'Moyen': 89, 'Élevé': 34}
        fig3 = px.bar(x=list(severity_data.keys()), y=list(severity_data.values()),
                      title="Répartition par niveau de sévérité",
                      color=list(severity_data.keys()),
                      color_discrete_map={'Faible': '#4ECDC4', 'Moyen': '#FFE66D', 'Élevé': '#FF6B6B'})
        st.plotly_chart(fig3, use_container_width=True)
    
    # Impact de l'application
    st.subheader("🎯 Impact de FoodSafe AI")
    
    impact_metrics = [
        {"metric": "Intoxications évitées", "value": "2,341", "description": "Grâce aux alertes précoces"},
        {"metric": "Économies générées", "value": "847K€", "description": "Coûts de santé évités"},
        {"metric": "Temps de réaction", "value": "< 2h", "description": "Alerte après détection du risque"},
        {"metric": "Précision des prédictions", "value": "92.7%", "description": "Taux de fiabilité de l'IA"}
    ]
    
    cols = st.columns(len(impact_metrics))
    for i, metric in enumerate(impact_metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4ECDC4; margin: 0;">{metric['value']}</h3>
                <h5 style="margin: 0.5rem 0;">{metric['metric']}</h5>
                <p style="font-size: 0.8rem; color: #666; margin: 0;">{metric['description']}</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()