import streamlit as st
import json
import pandas as pd
from pathlib import Path
path = Path(__file__).resolve().parent.parent / "reinforced_concrete"

# CLS
df_cls = pd.DataFrame(json.loads((path / "concrete_database.json").read_text()))

avaiable_cls_code_name = list(df_cls)
cls_code_name = st.selectbox(
    label="Normativa CLS",
    options=avaiable_cls_code_name,
    index=0,
    key="avaiable_cls_code_name",
)

avaiable_cls_concrete_type = list(df_cls[cls_code_name].index)

df_cls_code_name = pd.DataFrame(
    [df_cls[cls_code_name][concrete_type]for concrete_type in avaiable_cls_concrete_type]
)
st.dataframe(df_cls_code_name)

# STEEL
with open("reinforced_concrete/steel_database.json") as file:
    df_steel = pd.DataFrame(json.load(file))

avaiable_steel_code_name = list(df_steel)

steel_code_name = st.selectbox(
    label="Normativa Acciaio",
    options=avaiable_steel_code_name,
    index=0,
    key="avaiable_steel_code_name",
)

avaiable_steel_type = list(df_steel[steel_code_name].index)

df_steel_code_name = pd.DataFrame(
    [df_steel[steel_code_name][steel_type] for steel_type in avaiable_steel_type]
)
st.dataframe(df_steel_code_name)


#TODO questo nuovo dataframe sará quello che poi va nel resto dell'app.
#TODO da capire cosa succede se si cancella una riga. Viene poi ri-aggiunta al prossima riavvio?
test = st.data_editor(df_steel_code_name, hide_index=True, num_rows="dynamic", use_container_width=True)
st.dataframe(test, hide_index= True, use_container_width=True)
