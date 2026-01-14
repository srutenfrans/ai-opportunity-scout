import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuratie van de pagina
st.set_page_config(page_title="AI Opportunity Radar", layout="wide")

st.title("🚀 AI Opportunity Scout")
st.markdown("Vul de kenmerken van een proces in en zie direct waar het landt op de Gartner AI Radar.")

# 2. Sessie status (Zorgt dat data bewaard blijft tijdens de sessie)
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=[
        'Proces', 'Doelgroep', 'X_Positie', 'Y_Positie', 'Volume', 'Frustratie', 'Kwadrant'
    ])

# 3. De Invoer (Sidebar)
with st.sidebar:
    st.header("Nieuwe ERP Agent-Kans Scannen")
    
    name = st.text_input("Naam van de ERP-taak/proces", placeholder="Bijv. Automatische Boeking inkoopfacturen")
    
    # Y-As bepaling
    target = st.radio("Focusgebied van de taak?", ["Interne Transacties (Back Office)", "Besluitvorming/Planning (Core Capabilities)"])
    
    st.subheader("1. Agent Haalbaarheid")
    gestructureerdheid = st.slider("1. Gestructureerdheid Input", 1, 5, 3)
    regels_complexiteit = st.slider("2. Transactie-complexiteit", 1, 5, 3)
    generatieve_noodzaak = st.slider("3. Creativiteit/Generatie nodig?", 1, 5, 1)
    
    st.subheader("2. Prioriteit & Impact")
    frequentie_volume = st.slider("4. Frequentie & Volume", 1, 5, 3)
    frustratie = st.slider("5. Foutgevoeligheid/Frustratie", 1, 5, 1)
    
    # De "Plot" Knop
    if st.button("Plot op Radar"):
        # Berekening logica
        agent_simpelheid_score = (gestructureerdheid + regels_complexiteit) / 2
        
        # X-as positie (1 = Simpel, 5 = Complex)
        x_positie = (generatieve_noodzaak * 0.6) + (5 - agent_simpelheid_score) * 0.4
        x_positie = max(1, min(5, x_positie))

        # Y-as positie
        y_pos = 2.5 if target == "Interne Transacties (Back Office)" else 7.5
        
        # Bepaal Kwadrant
        kwadrant_grens = 3.0
        if target == "Interne Transacties (Back Office)":
            kwadrant = "Back Office Automatisering" if x_positie < kwadrant_grens else "Back Office AI"
        else:
            kwadrant = "Core Transacties" if x_positie < kwadrant_grens else "Strategische AI"

        # Maak nieuwe rij aan
        new_row = pd.DataFrame({
            'Proces': [name],
            'Doelgroep': [target],
            'X_Positie': [x_positie], 
            'Y_Positie': [y_pos], 
            'Volume': [frequentie_volume * 20], # Bolgrootte iets vergroot voor zichtbaarheid
            'Frustratie': [frustratie], 
            'Kwadrant': [kwadrant]
        })
        
        # VOEG TOE AAN DATASET
        st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)
        
        st.success(f"Proces '{name}' toegevoegd!")
        st.rerun()

# 4. Het Dashboard (Layout met kolommen)
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("De AI Radar")
    
    if not st.session_state['data'].empty:
        df = st.session_state['data']
        
     # Forceer Volume naar getallen om de 'narwhals' error te voorkomen
        df["Volume"] = pd.to_numeric(df["Volume"], errors='coerce')
        df["X_Positie"] = pd.to_numeric(df["X_Positie"], errors='coerce')
        df["Y_Positie"] = pd.to_numeric(df["Y_Positie"], errors='coerce')
        
        # Maak de Plotly Grafiek
        fig = px.scatter(
            df, 
            x="X_Positie", 
            y="Y_Positie",
            size="Volume", 
            color="Frustratie",
            hover_name="Proces",
            text="Proces",
            color_continuous_scale=["#00CC96", "#EF553B"],
            range_x=[0, 6],
            range_y=[0, 10],
            title="AI Agent Prioriteiten Matrix"
        )
        
        # Teken de kwadrant lijnen
        fig.add_hline(y=5, line_dash="dash", line_color="rgba(0,0,0,0.3)")
        fig.add_vline(x=3, line_dash="dash", line_color="rgba(0,0,0,0.3)")
        
        # Voeg de labels toe voor de 4 gebieden
        fig.add_annotation(x=1.5, y=1, text="<b>Back Office Automatisering</b>", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=4.5, y=1, text="<b>Back Office AI (Complex)</b>", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=1.5, y=9, text="<b>Core Transacties</b>", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=4.5, y=9, text="<b>Strategische AI</b>", showarrow=False, font=dict(color="gray"))

        fig.update_layout(
            xaxis_title="Complexiteit (AI Agent Sophistication)",
            yaxis_title="Focus (Back Office vs Core)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("De radar is nog leeg. Voer links een proces in en klik op 'Plot op Radar'.")

with col2:
    st.subheader("Prioriteitenlijst")
    if not st.session_state['data'].empty:
        # Toon tabel
        st.dataframe(st.session_state['data'][['Proces', 'Kwadrant', 'Business Pain']], hide_index=True)
        
        # Simpele AI-advies logica
        top_prio = st.session_state['data'].sort_values(by='Business Pain', ascending=False).iloc[0]
        st.warning(f"**Focus op:** {top_prio['Proces']}")
        st.write(f"Dit proces veroorzaakt de meeste frustratie.")
        
        if st.button("Lijst leegmaken"):
            st.session_state['data'] = pd.DataFrame(columns=st.session_state['data'].columns)
            st.rerun()


