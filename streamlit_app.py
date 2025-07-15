import streamlit as st
import pandas as pd

# Helper om HTML-blokken te tonen
def agent_block(title: str, color: str, feedback: str):
    st.markdown(
        f"""
        <div style="background-color:{color}; padding:16px; border-radius:8px; margin:16px 0;">
          <h4 style="color:white; margin:0;">{title}</h4>
          <pre style="color:white;">{feedback}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="AI Fiscale Jaarrekening", layout="centered")
st.title("🤖 AI Agent voor Fiscale Jaarrekening")
st.write("Upload je CSV (Grootboekrekening, Bedrag (EUR)) en zie de fiscale correcties.")

uploaded = st.file_uploader("📂 Kies je CSV-bestand", type=["csv"] )
if uploaded:
    try:
        # Inlees-agent
        agent_block("📥 Inlees-agent", "#22523b", "Controleren structuur en kolommen…")
        df = pd.read_csv(uploaded)

        # Validatie
        if not {"Grootboekrekening","Bedrag (EUR)"}.issubset(df.columns):
            st.error("CSV mist 'Grootboekrekening' of 'Bedrag (EUR)'")
        else:
            # Classificatie
            def bepaal_posttype(txt):
                t = txt.lower()
                if "representatie" in t: return "Representatiekosten"
                if "auto" in t:           return "Autokosten"
                if "huur" in t:           return "Huisvestingskosten"
                return "Overige kosten"
            df['Categorie'] = df['Grootboekrekening'].apply(bepaal_posttype)
            fb = []
            for i, r in df.iterrows():
                fb.append(f"Rij {i+1}: {r['Grootboekrekening']} → {r['Categorie']}")
            agent_block("🧠 Analyse-agent", "#3d405b", "\n".join(fb))

            # Correctie
            def corrigeer(r):
                b, c = r['Bedrag (EUR)'], r['Categorie']
                if c == "Representatiekosten":
                    toel = "80% aftrekbaar"
                    val = b * 0.8
                elif c == "Autokosten":
                    toel = "90% aftrekbaar"
                    val = b * 0.9
                else:
                    toel = "Volledig aftrekbaar"
                    val = b
                return val, b - val, toel

            res = df.apply(lambda row: corrigeer(row), axis=1, result_type='expand')
            df['Fiscaal aftrekbaar'], df['Correctie'], df['Toelichting'] = res[0], res[1], res[2]
            agent_block("⚖️ Correctie-agent", "#a14a76", "\n".join(df['Toelichting'].tolist()))

            st.success("✅ Fiscale berekening voltooid!")
            st.dataframe(df)

    except Exception as e:
        st.error(f"Fout bij inlezen: {e}")
