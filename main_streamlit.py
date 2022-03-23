import streamlit as st
import json
from reinforced_concrete.sections import create_concrete_material, create_steel_material, Bars, ReinforcedConcreteSection
from reinforced_concrete.ULS import computeVero

# -- GENERAL PAGE SETUP --
st.set_page_config(
     page_title = "Reinforced Concrete design",
     page_icon = "👷‍♂️",
     initial_sidebar_state = "collapsed",
     layout = "wide"
)
# -- SIDEBAR --

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
    avaiable_steel_concrete_type = list(json.load(file)[steel_code_name])
with col1_4:
    steel_type = st.selectbox(
            label = "Tipologia Acciaio", 
            options = avaiable_steel_concrete_type, 
            index= 0,
            key = "avaiable_steel_type"            
    ) 

# Selezione caratteristiche calcestruzzo
col2_1, col2_2, col2_3, col2_4 = st.columns(4)
with col2_1:
    b = st.number_input(
        label = "Base b [mm]",
        min_value = 1.,
        step = 50.,
        value=300.,
        format = "%.0f",
        key = "Base",
        )
with col2_2:
    d = st.number_input(
        label = "Altezza utile d [mm]",
        min_value = 1.,
        step = 10.,
        value=300.,
        format = "%.0f",
        key = "d",
        )
with col2_3:
    d1 = st.number_input(
        label = "Copriferro inferiore d1 [mm]",
        min_value = 1.,
        step = 5.,
        value=40.,
        format = "%.0f",
        key = "d1",
        )
with col2_4:
    d2 = st.number_input(
        label = "Copriferro superiore d2 [mm]",
        min_value = 1.,
        step = 5.,
        value=40.,
        format = "%.0f",
        key = "d2",
        )
# Selezione caratteristiche acciaio
col3_1, col3_2 ,col3_3, col3_4 = st.columns(4)
with col3_1:
    diam_bottom = int(st.number_input(
        label = "n. barre inferiori",
        min_value = 1,
        step = 1,
        value=2,
        key = "diam_bottom",
        ))
with col3_2:
    diam_bottom = int(st.number_input(
        label = "diametro barre inferiori [mm]",
        min_value = 2,
        step = 2,
        value=10,
        key = "diam_bottom",
        ))
with col3_3:
    diam_up = int(st.number_input(
        label = "n. barre superiori",
        min_value = 1,
        step = 1,
        value=2,
        key = "diam_up",
        ))
with col3_4:
    diam_up = int(st.number_input(
        label = "diametro barre superiori [mm]",
        min_value = 2,
        step = 2,
        value=10,
        key = "diam_up",
        ))
# Selezione sollecitazioni

col4_1, col4_2 = st.columns(2)
with col4_1:
    Med = st.number_input(
        label = "Momento [kNm]",
        min_value = 1.,
        step = 10.,
        value=100.,
        format = "%.6f",
        key = "Med",
        )
with col4_2:
    Ned = st.number_input(
        label = "Sforzo assiale [kN] (negativo se trazione)",
        min_value = 1.,
        step = 10.,
        value=100.,
        format = "%.6f",
        key = "Ned",
        )


cls  = create_concrete_material(cls_code_name,concrete_type) 
steel  = create_steel_material(steel_code_name,steel_type)
st.write(cls)
st.write(steel)
As = Bars(n_bars=diam_bottom, diameter=diam_bottom, steel_material=steel)
As1 = Bars(n_bars=diam_up, diameter=diam_up, steel_material=steel)
section = ReinforcedConcreteSection(b=b, d=d, d1=d1, d2=d2, concrete_material=cls, As=As, As1=As1, name="sec1")

results_dict, logs = computeVero(Med=Med*10**6, Ned=Ned, section=section)

st.write(section.__repr__())
st.write(results_dict)
for log in logs:
    st.write(log)