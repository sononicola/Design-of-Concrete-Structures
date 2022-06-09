import streamlit as st
import json
import pandas as pd

# CLS
with open("reinforced_concrete/concrete_database.json") as file:
    df_cls = pd.DataFrame(json.load(file))

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
