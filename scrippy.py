import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuratie van de pagina
st.set_page_config(page_title="AI Opportunity Radar", layout="wide")

st.title("🚀 AI Opportunity Scout")
st.markdown("Vul de kenmerken van een proces in en zie direct waar het landt op de Gartner AI Radar.")

# 2. Sessie status (om data te onthouden zolang de app open staat)
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=[
        'Proces', 'Type', 'Complexiteit', 'Impact', 'Frustratie', 'AI_Score', 'Quadrant'
    ])

# 3. De Invoer (Sidebar)
with st.sidebar:
    st.header("Nieuwe ERP Agent-Kans Scannen")
    
    name = st.text_input("Naam van de ERP-taak/proces", "Bijv. Automatische Boeking van inkoopfacturen")
    
    # Y-As: Doelgebied binnen het ERP
    target = st.radio("Focusgebied van de taak?", ["Interne Transacties (Back Office)", "Besluitvorming/Planning (Core Capabilities)"])
    
    # --- ERP AGENT-GESCHIKTHEID (Bepalen Implementatiemoeilijkheid / X-as) ---
    st.subheader("1. Agent Haalbaarheid (Technisch & Gestructureerdheid)")
    # Vragen die bepalen hoe 'moeilijk' (Game-Changing) de Agent is:
    
    # Vraag 1: Gestructureerdheid van de input (ERP-velden, vaste formaten)
    gestructureerdheid = st.slider("1. Gestructureerdheid Input", 1, 5, 3, help="Hoe gestandaardiseerd zijn de data en invoer in het ERP (5=Erg vast, 1=Veel vrije tekst)?")
    
    # Vraag 2: Complexiteit van de te volgen regels
    regels_complexiteit = st.slider("2. Transactie-complexiteit", 1, 5, 3, help="Hoe complex zijn de bedrijfsregels of workflows die de Agent moet volgen (5=Duidelijke stappen, 1=Veel uitzonderingen)?")
    
    # Vraag 3: Noodzaak voor generatieve AI
    generatieve_noodzaak = st.slider("3. Creativiteit/Generatie nodig?", 1, 5, 1, help="Moet de Agent zelf teksten, antwoorden of unieke code genereren (5=Ja, 1=Nee)?")
    
    st.subheader("2. Prioriteit & Impact (Bepalen Volume & Urgentie)")
    # Deze bepalen de Grootte (Volume) en Kleur (Frustratie)
    
    # Vraag 4: Frequentie/Volume (Bepaalt de ROI/Bolgrootte)
    frequentie_volume = st.slider("4. Frequentie & Volume", 1, 5, 3, help="Hoe vaak en hoeveel tijd wordt aan deze taak besteed (5=Dagelijkse, hoge volumes)?")
    
    # Vraag 5: Foutgevoeligheid/Frustratie (Bepaalt Kleur/Urgentie)
    frustratie = st.slider("5. Foutgevoeligheid/Frustratie", 1, 5, 1, help="Hoe vaak gaat dit mis of veroorzaakt het irritatie bij de eindgebruiker (5=Hoog)?")
    
    # Knop om toe te voegen
    if st.button("Plot op Radar"):
        
        # --- BEREKENING LOGICA (Aangepast voor Agent Focus) ---
        
        # 1. Bepaal de "Agent Simpelheid" Score:
        # Een hoge score hier betekent dat de taak gestructureerd en eenvoudig is.
        agent_simpelheid_score = (gestructureerdheid + regels_complexiteit) / 2
        
        # 2. Bepaal de X-AS POSITIE: "Implementatiemoeilijkheid"
        # X-as loopt van Eenvoudig (Links) naar Complex (Rechts).
        # Een hoge 'generatieve noodzaak' en een lage 'agent simpelheid' duwen naar rechts (Complex).
        
        # De X-Positie wordt bepaald door de combinatie van complexiteit en de generatieve behoefte.
        # We normaliseren de score zodat deze tussen 1 en 5 ligt.
        
        # Hier gebruiken we de Generatieve noodzaak direct als indicator voor complexiteit,
        # en compenseren we met hoe simpel de taak is.
        
        # Simpele, repetitieve taken (Hoge Agent Simpelheid, Lage Generatieve Noodzaak) gaan naar Links (X=1-3).
        # Complexe, generatieve taken (Lage Agent Simpelheid, Hoge Generatieve Noodzaak) gaan naar Rechts (X=3-5).
        
        # Formule om X-positie te bepalen (gewogen gemiddelde, gericht op complexiteit):
        x_positie = (generatieve_noodzaak * 0.6) + (5 - agent_simpelheid_score) * 0.4
        
        # Zorg dat de score binnen het bereik [1, 5] blijft
        x_positie = max(1, min(5, x_positie))

        # Y-as positie
        # Back Office = 2.5 (Laag) | Core Capabilities = 7.5 (Hoog)
        y_pos = 2.5 if target == "Interne Transacties (Back Office)" else 7.5
        
        # Bepaal Kwadrant naam
        kwadrant_grens = 3.0 # Scheidslijn X=3 in de plot
        
        if target == "Interne Transacties (Back Office)":
            kwadrant = "Back Office Automatisering (Eenvoudig)" if x_positie < kwadrant_grens else "Back Office AI (Complex)"
        else:
            kwadrant = "Core Transacties (Eenvoudig)" if x_positie < kwadrant_grens else "Strategische AI (Complex)"

        new_row = pd.DataFrame({
            'Proces': [name],
            'Doelgroep': [target],
            'Everyday_Score': [agent_simpelheid_score], # Hergebruik van de kolomnaam voor Simpelheid
            'GameChange_Score': [generatieve_noodzaak], # Hergebruik van de kolomnaam voor Generatie
            'X_Positie': [x_positie], 
            'Y_Positie': [y_pos], 
            'Volume': [frequentie_volume * 10], # Grootte van de bol
            'Frustratie': [frustratie], # Kleur
            'Kwadrant': [kwadrant]
        })
        
        # ... (De rest van uw logica voor het toevoegen aan st.session_state of Google Sheets)
        # st.session_state['data'] = pd.concat(...)
        # conn.write(...)
        st.success(f"Proces '{name}' geplot op de Agent Radar.")

# 4. Het Dashboard (Rechterkant)
# In Sectie 4: fig.update_layout
fig.update_layout(
    xaxis_title="Implementatiemoeilijkheid AI Agent (Links=Eenvoudig, Rechts=Complex)",
    yaxis_title="Focus Gebied (Lage Y=Back Office, Hoge Y=Core Capabilities)",
    showlegend=True
)

# In Sectie 4: fig.add_annotation
fig.add_annotation(x=2.0, y=2.5, text="<b>Back Office Automatisering</b><br>(Simpele Agents)", showarrow=False)
fig.add_annotation(x=4.0, y=2.5, text="<b>Back Office AI</b><br>(Complexe Agents/LLMs)", showarrow=False)
fig.add_annotation(x=2.0, y=7.5, text="<b>Core Transacties</b><br>(Simpele Agents)", showarrow=False)
fig.add_annotation(x=4.0, y=7.5, text="<b>Strategische AI</b><br>(Complexe Agents/Generatie)", showarrow=False)

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("De AI Radar")
    
    if not st.session_state['data'].empty:
        df = st.session_state['data']
        
        # Plotly Grafiek
        fig = px.scatter(
            df, 
            x="X_Positie", 
            y="Y_Positie",
            size="Volume", 
            color="Frustratie",
            hover_name="Proces",
            text="Proces",
            color_continuous_scale=["green", "yellow", "red"],
            range_x=[0, 6],
            range_y=[0, 10],
            title="AI Prioriteiten Matrix"
        )
        
        # De 4 kwadranten tekenen (Lijnen)
        fig.add_hline(y=5, line_dash="dash", line_color="gray", annotation_text="Scheidslijn Intern / Extern")
        fig.add_vline(x=3, line_dash="dash", line_color="gray", annotation_text="Scheidslijn Everyday / Game-Changing")
        
        # Labels voor de kwadranten
        fig.add_annotation(x=1.5, y=2.5, text="<b>Back Office</b><br>(Everyday)", showarrow=False)
        fig.add_annotation(x=4.5, y=2.5, text="<b>Core Capabilities</b><br>(Game Changing)", showarrow=False)
        fig.add_annotation(x=1.5, y=7.5, text="<b>Front Office</b><br>(Everyday)", showarrow=False)
        fig.add_annotation(x=4.5, y=7.5, text="<b>Products/Services</b><br>(Game Changing)", showarrow=False)

        fig.update_layout(
            xaxis_title="Mate van Innovatie (Game Changing)",
            yaxis_title="Focus Gebied (Intern vs Extern)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Voer links je eerste proces in om de radar te starten!")

with col2:
    st.subheader("Lijst & Prioriteiten")
    if not st.session_state['data'].empty:
        # Toon alleen de interessante kolommen
        display_df = st.session_state['data'][['Proces', 'Kwadrant', 'Frustratie']]
        st.dataframe(display_df, hide_index=True)
        
        st.markdown("### 💡 Advies")
        top_prio = st.session_state['data'].sort_values(by=['Frustratie', 'Volume'], ascending=False).iloc[0]
        st.warning(f"**Hoogste Prioriteit:** {top_prio['Proces']}")

        st.write(f"Dit proces scoort hoog op frustratie ({top_prio['Frustratie']}/5). Kijk hier eerst naar!")
