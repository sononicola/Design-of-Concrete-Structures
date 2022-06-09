import streamlit as st

import json
from reinforced_concrete.sections import create_concrete_material, create_steel_material

from dataclasses import asdict
import pandas as pd

from reinforced_concrete import design

# -- GENERAL PAGE SETUP --
st.set_page_config(
     page_title = "Reinforced Concrete design",
     page_icon = "👷‍♂️",
     initial_sidebar_state = "expanded",
     layout = "wide"
)

# -- PAGE CONTENT --
st.title("Design of Reinforced Concrete section")


# Selezione dei materiali prendendo le liste dai database json
col1_1, col1_2, col1_3, col1_4 = st.columns(4)
# CLS
with open("reinforced_concrete/concrete_database.json") as file:
    avaiable_cls_code_name = list(json.load(file))
with col1_1:
    cls_code_name = st.selectbox(
            label = "Normativa CLS", 
            options = avaiable_cls_code_name, 
            index= 0,
            key = "avaiable_cls_code_name"            
    ) 
with open("reinforced_concrete/concrete_database.json") as file:
    avaiable_cls_concrete_type = list(json.load(file)[cls_code_name])
with col1_2:
    concrete_type = st.selectbox(
            label = "Tipologia CLS", 
            options = avaiable_cls_concrete_type, 
            index= 3,
            key = "avaiable_concrete_type"            
    ) 
# STEEL
with open("reinforced_concrete/steel_database.json") as file:
    avaiable_steel_code_name = list(json.load(file))
with col1_3:
    steel_code_name = st.selectbox(
            label = "Normativa Acciaio", 
            options = avaiable_steel_code_name, 
            index= 0,
            key = "avaiable_steel_code_name"            
    ) 
with open("reinforced_concrete/steel_database.json") as file:
    avaiable_steel_type = list(json.load(file)[steel_code_name])
with col1_4:
    steel_type = st.selectbox(
            label = "Tipologia Acciaio", 
            options = avaiable_steel_type, 
            index= 0,
            key = "avaiable_steel_type"            
    ) 


cls  = create_concrete_material(cls_code_name,concrete_type) 
steel  = create_steel_material(steel_code_name,steel_type)
#Bottone per cambiare il modulo elastico dell'acciaio
change_Es = st.checkbox(f"Vuoi cambiare il modulo elastico? Attualmente vale {steel.Es/1000} Gpa")
if change_Es:
    steel.Es = 1000*st.number_input(
        label = "Nuovo valore di Es [Gpa]",
        step = 1.,
        value=210.,
        format = "%.1f",
        key = "Es",
        )


# Selezione sollecitazioni
col4_1, col4_2 = st.columns(2)
with col4_1:
    Med = st.number_input(
        label = "Momento [kNm]",
        step = 10.,
        value=100.,
        format = "%.6f",
        key = "Med",
        )
with col4_2:
    Ned = st.number_input(
        label = "Sforzo assiale [kN] (negativo se trazione)",
        step = 10.,
        value=100.,
        format = "%.6f",
        key = "Ned",
        )

section_geometry = st.radio("Scegli la forma della sezione", options=("Rettangolare", "T"))

if section_geometry == "Rettangolare":
    design_constrain = st.radio("Scegli il vincolo per il progetto", options=("Base fissata", "Altezza utile fissata"))
    col3_1, col3_2, col3_3, col3_4 = st.columns(4)
    if design_constrain == "Base fissata":
        with col3_1 :
            beta = st.number_input(
            label = "beta = As/As1",
            min_value = 0.,
            max_value=1.0,
            step = .1,
            value=.5,
            format = "%.1f",
            key = "beta",
            )
        with col3_2:
            b = st.number_input(
                label = "Base b [mm]",
                min_value = 1.,
                step = 50.,
                value=300.,
                format = "%.0f",
                key = "Base",
                )
        with col3_3:
            d1 = st.number_input(
                label = "Copriferro inferiore d1 [mm]",
                min_value = 1.,
                step = 5.,
                value=40.,
                format = "%.1f",
                key = "d1",
                )
        with col3_4:
            d2 = st.number_input(
                label = "Copriferro superiore d2 [mm]",
                min_value = 1.,
                step = 5.,
                value=40.,
                format = "%.1f",
                key = "d2",
                )
        As, d = design.design_b_constrain(cls=cls, steel=steel, beta=beta, b=b, Med=Med*10**6, d2= d2)
        st.subheader("Soluzione:")

        st.write(f"As = {As:.2f} mm2") 
        st.write(f"As1 = {As*beta:.2f} mm2") 
        st.write(f"d = {d:.2f} mm") 

        st.subheader("Possibili scelte:")
        for diam in [12, 14, 16, 18, 20, 22]:
            n = 1 + int(As / (3.14 * diam ** 2 / 4))
            st.write(f"{n:>2}Ø{diam} = {n * 3.14 * diam**2 / 4:.2f} mm2")





    elif design_constrain == "Altezza utile fissata":
        with col3_1 :
            beta = st.number_input(
                label = "beta = As/As1",
                min_value = 0.,
                max_value=1.0,
                step = .1,
                value=.5,
                format = "%.2f",
                key = "beta",
                )
        with col3_2:
            d = st.number_input(
                label = "Altezza utile d [mm]",
                min_value = 1.,
                step = 10.,
                value=300.,
                format = "%.1f",
                key = "d",
                )
        with col3_3:
            d1 = st.number_input(
                label = "Copriferro inferiore d1 [mm]",
                min_value = 1.,
                step = 5.,
                value=40.,
                format = "%.1f",
                key = "d1",
                )
        with col3_4:
            d2 = st.number_input(
                label = "Copriferro superiore d2 [mm]",
                min_value = 1.,
                step = 5.,
                value=40.,
                format = "%.1f",
                key = "d2",
                    )






st.sidebar.write(repr(cls))
st.sidebar.write(repr(steel))