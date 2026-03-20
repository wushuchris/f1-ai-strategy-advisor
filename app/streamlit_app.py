import streamlit as st

st.set_page_config(
    page_title="F1 AI Strategy Advisor",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 AI Strategy Advisor")

st.write("🚀 This is the beginning of a real-time IoT + AI strategy system.")

st.subheader("System Status")
st.success("Streamlit app is running successfully.")

st.subheader("What’s Coming Next")
st.markdown("""
- 📡 Simulated IoT telemetry stream  
- 📊 Predictive models (tire degradation, lap performance)  
- 🧠 AI-generated race strategy recommendations  
- 🏁 Real-time dashboard  
""")
