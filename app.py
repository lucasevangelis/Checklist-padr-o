import streamlit as st

st.set_page_config(page_title="Sistema de Pisos", page_icon="🏢", layout="centered")

st.title("🏢 Sistema de Controle de Pisos")
st.markdown("Bem-vindo ao sistema integrado de controle e monitoramento de pisos.")
st.markdown("""
### O que você deseja fazer?

👈 **Use o menu lateral esquerdo para navegar:**

- 📊 **Dashboard:** Visualize gráficos, métricas e análises dos dados já coletados.
- 📝 **Registro Checklist:** Registre novas ocorrências e observações online.
- 📲 **Modo Offline:** Use o novo aplicativo para coletar dados mesmo sem internet no celular.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📲 App de Celular")
st.sidebar.info("Para coletar dados em locais sem internet, utilize o nosso **Aplicativo Offline**.")
if st.sidebar.button("Acessar App Offline"):
    st.info("Para usar no celular, abra o link do seu GitHub Pages (Ex: lucasevangelis.github.io/Checklist-padr-o/coleta_offline/)")
