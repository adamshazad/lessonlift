import streamlit as st
from openai import OpenAI

st.title("Available Models")

try:
    client = OpenAI()
    models = client.models.list()

    st.write("### Models you have access to:")
    for m in models.data:
        st.write(m.id)

except Exception as e:
    st.error(str(e))
