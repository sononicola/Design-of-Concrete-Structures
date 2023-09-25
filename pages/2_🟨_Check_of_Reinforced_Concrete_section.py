import streamlit as st

import json
from reinforced_concrete.sections import (
    create_concrete_material,
    create_steel_material,
    Bars,
    ReinforcedConcreteSection,
    InternalForces,
    Stirrups,
)
from reinforced_concrete.ULS import computeVero
from reinforced_concrete.sls import sls
from reinforced_concrete.shear import (
    shear_only_cls_layer,
    shear_with_specific_armor_layer,
)
from reinforced_concrete.design import minimum_section_base

from dataclasses import asdict
import pandas as pd

from pathlib import Path

path = Path(__file__).resolve().parent.parent / "reinforced_concrete"

# -- GENERAL PAGE SETUP --
st.set_page_config(
    page_title="Reinforced Concrete design",
    page_icon="👷‍♂️",
    initial_sidebar_state="expanded",
    layout="wide",
)

# -- PAGE CONTENT --
st.title("Check of Reinforced Concrete section")


# Selezione dei materiali prendendo le liste dai database json
col1_1, col1_2, col1_3, col1_4 = st.columns(4)
# CLS

avaiable_cls_code_name = list(json.loads((path / "concrete_database.json").read_text()))
with col1_1:
    cls_code_name = st.selectbox(
        label="Normativa CLS",
        options=avaiable_cls_code_name,
        index=0,
        key="avaiable_cls_code_name",
    )
avaiable_cls_concrete_type = list(
    json.loads((path / "concrete_database.json").read_text())[cls_code_name]
)

with col1_2:
    concrete_type = st.selectbox(
        label="Tipologia CLS",
        options=avaiable_cls_concrete_type,
        index=3,
        key="avaiable_concrete_type",
    )
# STEEL
avaiable_steel_code_name = list(json.loads((path / "steel_database.json").read_text()))

with col1_3:
    steel_code_name = st.selectbox(
        label="Normativa Acciaio",
        options=avaiable_steel_code_name,
        index=0,
        key="avaiable_steel_code_name",
    )
avaiable_steel_type = list(
    json.loads((path / "steel_database.json").read_text())[steel_code_name]
)

with col1_4:
    steel_type = st.selectbox(
        label="Tipologia Acciaio",
        options=avaiable_steel_type,
        index=0,
        key="avaiable_steel_type",
    )
cls = create_concrete_material(cls_code_name, concrete_type)
steel = create_steel_material(steel_code_name, steel_type)
# Bottone per cambiare il modulo elastico dell'acciaio
change_Es = st.checkbox(
    f"Vuoi cambiare il modulo elastico? Attualmente vale {steel.Es/1000} Gpa"
)
if change_Es:
    steel.Es = 1000 * st.number_input(
        label="Nuovo valore di Es [Gpa]",
        step=1.0,
        value=210.0,
        format="%.1f",
        key="Es",
    )
st.divider()

# Selezione caratteristiche calcestruzzo
col2_1, col2_2, col2_3, col2_4 = st.columns(4)
with col2_1:
    b = st.number_input(
        label="Base b [mm]",
        min_value=1.0,
        step=50.0,
        value=300.0,
        format="%.0f",
        key="Base",
    )
with col2_2:
    d = st.number_input(
        label="Altezza utile d [mm]",
        min_value=1.0,
        step=10.0,
        value=300.0,
        format="%.1f",
        key="d",
    )
with col2_3:
    d1 = st.number_input(
        label="Copriferro inferiore d1 [mm]",
        min_value=1.0,
        step=5.0,
        value=40.0,
        format="%.1f",
        key="d1",
    )
with col2_4:
    d2 = st.number_input(
        label="Copriferro superiore d2 [mm]",
        min_value=1.0,
        step=5.0,
        value=40.0,
        format="%.1f",
        key="d2",
    )
# Selezione caratteristiche acciaio
col3_1, col3_2, col3_3, col3_4 = st.columns(4)
with col3_1:
    n_bars_bottom = int(
        st.number_input(
            label="n. barre inferiori",
            min_value=1,
            step=1,
            value=2,
            key="n_bars_bottom",
        )
    )
with col3_2:
    diam_bottom = int(
        st.number_input(
            label="diametro barre inferiori [mm]",
            min_value=2,
            step=2,
            value=10,
            key="diam_bottom",
        )
    )
with col3_3:
    n_bars_up = int(
        st.number_input(
            label="n. barre superiori",
            min_value=1,
            step=1,
            value=2,
            key="n_bars_up",
        )
    )
with col3_4:
    diam_up = int(
        st.number_input(
            label="diametro barre superiori [mm]",
            min_value=2,
            step=2,
            value=10,
            key="diam_up",
        )
    )

# Selezione caratteristiche staffe
col5_1, col5_2, col5_3, col5_4 = st.columns(4)
with col3_1:
    n_braces = int(
        st.number_input(
            label="n. bracci staffe",
            min_value=2,
            step=1,
            value=2,
            key="n_braces",
        )
    )
with col3_2:
    diam_stirrups = int(
        st.number_input(
            label="diametro staffe [mm]",
            min_value=2,
            step=2,
            value=8,
            key="diam_stirrups",
        )
    )
with col3_3:
    s_stirrups = int(
        st.number_input(
            label="passo staffe [mm]",
            min_value=40,
            step=10,
            value=140,
            key="s_stirrups",
        )
    )

st.divider()
# Selezione sollecitazioni
col4_1, col4_2 = st.columns(2)
with col4_1:
    Med = st.number_input(
        label="Momento [kNm]",
        step=10.0,
        value=100.0,
        format="%.6f",
        key="Med",
    )
with col4_2:
    Ned = st.number_input(
        label="Sforzo assiale [kN] (negativo se trazione)",
        step=10.0,
        value=100.0,
        format="%.6f",
        key="Ned",
    )

# Baee minima
st.divider()
col5_1, col5_2 = st.columns(2) 
with col5_1:
    c_min = st.number_input(
                label = "Copriferro c_min [mm]",
                min_value = 1.,
                step = 1.,
                value=35.,
                format = "%.0f",
                key = "c_min",
                )
with col5_2:
    interferro = st.number_input(
                label = "Interferro [mm]",
                min_value = 1.,
                step = 1.,
                value=25.,
                format = "%.0f",
                key = "interferro",
                )
b_min = minimum_section_base(n_bars_bottom, diam_bottom, diam_stirrups, c_min, interferro)
st.markdown("$b_{min} = 2 \cdot c_{min} + 2\cdot Ø_{stirrups} + n_{bars}\cdot Ø_{bars} + i\cdot (n_{bars} - 1) = $"+ f"{b_min:.0f} mm < b = {b:.0f} mm | {b_min < b}")
st.divider()



As = Bars(n_bars=n_bars_bottom, diameter=diam_bottom, steel_material=steel)
As1 = Bars(n_bars=n_bars_up, diameter=diam_up, steel_material=steel)
forces = InternalForces(M=Med * 10**6, N=Ned * 10**3)
stirrups = Stirrups(
    n_braces=n_braces,
    diameter=diam_stirrups,
    spacing=s_stirrups,
    alpha=90,
    steel_material=steel,
)  # TODO alpha e alpha c fuori
section = ReinforcedConcreteSection(
    b=b,
    d=d,
    d1=d1,
    d2=d2,
    concrete_material=cls,
    As=As,
    As1=As1,
    internal_forces=forces,
    stirrups=stirrups,
)

st.sidebar.write("Repr of objects:")
st.sidebar.code(repr(section))

# -- RUNNING PROGRAM --
results_ULS, logs_ULS = computeVero(section=section)
results_SLS, logs_SLS = sls(section=section)
results_ULS_shear_no_armor = shear_only_cls_layer(section=section)
results_ULS_shear_with_armor = shear_with_specific_armor_layer(
    section=section, alpha_c=1
)
st.sidebar.divider()
st.sidebar.metric("b_min", f"{round(b_min)} mm")
st.sidebar.metric("Mrd", f"{round(results_ULS.get('Mrd')/1000000,2)} kNm")
st.sidebar.metric("Vrd no armor", f"{round(results_ULS_shear_no_armor.get('Vrd')/1000,2)} kN")
st.sidebar.metric("Vrd with armor", f"{round(results_ULS_shear_with_armor.get('Vr_d')/1000,2)} kN")
col5_1, col5_2 = st.columns(2)
with col5_1:
    st.subheader("Input:")
    st.text(section)
    st.write(asdict(section))

with col5_2:
    st.subheader("ULS:")
    st.write(results_ULS)
    st.text(logs_ULS)

    st.subheader("SLS:")
    st.write(results_SLS)
    st.text(logs_SLS)

    st.subheader("Shear only CLS:")
    st.write(results_ULS_shear_no_armor)

    st.subheader("Shear with armor:")
    st.write(results_ULS_shear_with_armor)

# print(asdict(section))
# print(results_dict)
