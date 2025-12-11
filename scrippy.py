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
    st.header("Nieuw Proces Scannen")
    
    name = st.text_input("Naam van het proces", "Bijv. Factuurverwerking")
    
    # Gartner Y-As: Intern vs Extern
    target = st.radio("Wie is de doelgroep?", ["Intern (Operaties)", "Extern (Klanten/Product)"])
    
    st.subheader("Everyday AI Check (Automatisering)")
    repetitie = st.slider("Hoe repetitief is het?", 1, 5, 3)
    regels = st.slider("Zijn er vaste regels?", 1, 5, 3)
    tijd = st.slider("Hoeveel tijd kost het (Volume)?", 1, 5, 3) # Bepaalt bolgrootte
    frustratie = st.slider("Mate van frustratie?", 1, 5, 1) # Bepaalt kleur (rood is erg)
    
    st.subheader("Game-Changing AI Check (Innovatie)")
    data_int = st.slider("Is het data-intensief?", 1, 5, 1)
    creatief = st.slider("Is creativiteit/generatie nodig?", 1, 5, 1)
    
    # Knop om toe te voegen
    if st.button("Plot op Radar"):
        # Logica: Bereken scores
        # Everyday Score (gemiddelde van repetitie en regels)
        everyday_score = (repetitie + regels) / 2
        
        # Game Changing Score (gemiddelde van data en creativiteit)
        game_changing_score = (data_int + creatief) / 2
        
        # De uiteindelijke X-as positie op de radar (Alledaags vs Baanbrekend)
        # We maken een schaal van 0 (Puur Everyday) tot 10 (Puur Game Changing)
        # Als Game Changing hoog is, duwt dat de score naar rechts.
        ai_complexity_score = (game_changing_score * 2) - (everyday_score * 0.5) 
        # (Dit is een simpele weging, kun je aanpassen)
        
        # Y-as positie (Intern vs Extern)
        # We geven Intern een waarde 1-5 en Extern 6-10 voor de visualisatie
        y_pos = 2.5 if target == "Intern (Operaties)" else 7.5
        
        # Bepaal Kwadrant naam
        if target == "Intern (Operaties)":
            kwadrant = "Back Office (Everyday)" if game_changing_score < 3 else "Core Capabilities (Game Changing)"
        else:
            kwadrant = "Front Office (Everyday)" if game_changing_score < 3 else "Product/Service (Game Changing)"

        new_row = pd.DataFrame({
            'Proces': [name],
            'Doelgroep': [target],
            'Everyday_Score': [everyday_score],
            'GameChange_Score': [game_changing_score],
            'X_Positie': [game_changing_score], # Simpele mapping: X-as is mate van "Game Changing"
            'Y_Positie': [y_pos], 
            'Volume': [tijd * 10], # Grootte van de bol
            'Frustratie': [frustratie], # Kleur
            'Kwadrant': [kwadrant]
        })
        
        st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)

# 4. Het Dashboard (Rechterkant)
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