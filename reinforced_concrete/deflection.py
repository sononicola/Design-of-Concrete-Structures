import sympy as sp
from scipy.integrate import quad, simpson
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import ArrayLike

from reinforced_concrete.sections import (
    create_concrete_material,
    create_steel_material,
    Bars,
    ReinforcedConcreteSection,
    InternalForces,
    Stirrups,
)


def zeta(m_cr: float, m_Q: ArrayLike, beta: float) -> ArrayLike:
    with np.errstate(divide="ignore", invalid="ignore"):  # altrimenti rompe il cazzo quando si divide per zero
        zeta = 1 - beta * (m_cr / m_Q) ** 2
    if zeta is np.nan: # altrimento continua a dare NaN fino al risultato finale
        return 1 - beta
    return zeta


# nope solo se  MQ è parabolico
def chi(
    m_cr: float, m_Q: sp.Function, Inn_1: float, c: float, Ecm: float, beta: float
) -> sp.Function:
    "c: Inn_2/Inn_1. c=1 se non fessurata e quindi rimane solo chi_1"
    chi_1 = m_Q / (Ecm * Inn_1)
    return (
        chi_1 if c == 1 else chi_1 * (1 + zeta(m_cr=m_cr, m_Q=m_Q, beta=beta) * (c - 1))
    )


def chi_np(
    m_cr: float, m_Q: ArrayLike, Inn_1: float, c: float, Ecm: float, beta: float
) -> ArrayLike:
    """
    c: Inn_2/Inn_1. c=1 se non fessurata e quindi rimane solo chi_1
    m_Q è il vettore che plotta il diagramma reale del momento con la combinazione che genera il massimo momento di campata, non l'inviluppo
    """
    chi_1: ArrayLike = m_Q / (Ecm * Inn_1)

    zeta_vero = zeta(m_cr=m_cr, m_Q=m_Q, beta=beta)
    if zeta_vero is np.inf or -np.inf:
        zeta_vero = 0

    with np.errstate(divide="ignore", invalid="ignore"):  # altrimenti rompe il cazzo quando si divide per zero
        chi = (chi_1 if c == 1 else chi_1 * (1 + zeta_vero * (c - 1)))
    return chi


def calc_c(m_ed: float, m_cr: float, Inn_1: float, Inn_2: float) -> float:
    return 1 if abs(m_ed) <= abs(m_cr) else Inn_1 / Inn_2


def deformazione(
    m_ed: float,
    m_cr: float,
    m_Q: ArrayLike,
    xi_a: float,
    xi_b: float,
    xi_max: float,
    Q: float,
    L: float,
    Inn_1: float,
    Inn_2: float,
    Ecm: float,
    beta: float,
):
    xi = sp.symbols("xi")

    R_sx = (L - xi_max) / L
    R_dx = xi_max / L
    M_sx = -R_sx * xi
    M_dx = -R_sx * xi + (xi - xi_max)
    if xi_a <= xi_max and xi_b <= xi_max:
        m_F = M_sx
        print("M_sx")
    elif xi_a >= xi_max and xi_b >= xi_max:
        m_F = M_dx
        print("M_dx")
    elif (xi_a < xi_max) and (xi_b > xi_max):
        raise ValueError(
            f"i due estremi di integrazione devono stare o entrambi a sinistra o entrambi a destra di xi_max {xi_a = }, {xi_max = }, {xi_b = }"
        )
    print(f"{m_F = }")

    # m_Q = Q*(L*xi/2 - xi**2/2)
    # print(f"{m_Q = }")

    c = calc_c(m_ed=m_ed, m_cr=m_cr, Inn_1=Inn_1, Inn_2=Inn_2)
    print(f"{c = }")

    chi_vera = chi_np(m_cr=m_cr, m_Q=m_Q[xi_a:xi_b], Inn_1=Inn_1, c=c, Ecm=Ecm, beta=beta)
    print(f"{chi_vera = }")
    print(f"{xi_a = :_.0f} | {xi_b = :_.0f}| {Inn_1 = :_.0f}| {Inn_2 = :_.0f}")
    # return sp.integrate(chi_vera*m_F, (xi, xi_a, xi_b))
    # return quad(sp.lambdify(xi, chi_vera*m_F), xi_a, xi_b)[0]
    m_F_f = sp.lambdify(xi, m_F)
    m_F_np = m_F_f(np.linspace(xi_a, xi_b, num=xi_b-xi_a))
    return simpson(chi_vera * m_F_np)


# delta = deformazione(m_ed=40e6, m_cr=36.91e6, xi_a=798, xi_b=1965, xi_max=1965, Q=50, L=4_960, Inn_1=1_514_424_394, Inn_2=978_984_614, Ecm=32_836.57, beta=0.5)
# print(f"{delta = }")
#
# print("---")
#
# delta = deformazione(m_ed=40e6, m_cr=36.91e6, xi_a=1965, xi_b=3133, xi_max=1965, Q=50, L=4_960, Inn_1=1_514_424_394, Inn_2=978_984_614, Ecm=32_836.57, beta=0.5)
# print(f"{delta = }")


def deflection_ReinforcedConcreteSection(
    m_Q: ArrayLike,
    list_of_sections: list[ReinforcedConcreteSection],
    list_of_xi_coords: list,
    xi_max: float,
    load: float,
    span_lenght: float,
    beta: float,
    coef_fctm=1,
    n: float = 15,
    n1: float = 1,
) -> dict:
    """
    xi_max:  axciss where there is the max M_ed value. This axciss must be also inside the list_of_coords!
    coef_fctm: 1.2 if want sigma_ctm = fctm/1.2, or 1 if not
    """
    if len(list_of_sections) != len(list_of_xi_coords) - 1:
        raise ValueError(
            f"La lunghezza della lista dei punti di ascissa deve essere n+1 quella della lista delle sezioni"
        )
    if xi_max not in list_of_xi_coords:
        raise ValueError(
            f"La coordinata xi_max deve anche essere dentro alla lista di coordinate list_of_xi_coords.\nTale valore viene usato per determinare se usare M_sx o M_dx"
        )

    list_of_delta = []
    for section, i in zip(list_of_sections, range(len(list_of_xi_coords) - 1)):
        delta = deformazione(
            m_ed=section.internal_forces.M,
            m_cr=section.m_cr(coef_fctm=coef_fctm, n=n, n1=n1),
            m_Q=m_Q,
            xi_a=list_of_xi_coords[i],
            xi_b=list_of_xi_coords[i + 1],
            xi_max=xi_max,
            Q=load,
            L=span_lenght,
            Inn_1=section.Inn_1(n=n, n1=n1),
            Inn_2=section.Inn_2(n=n),
            Ecm=section.concrete_material.Ecm,
            beta=beta,
        )

        print(section.name)
        print(f"{section.m_cr(coef_fctm=coef_fctm, n=n, n1=n1) = :_.0f}")
        print(" =============== ")
        list_of_delta.append(delta)

    return list_of_delta


def main():
    xi_coords = [0, 798, 1965, 3133]
    m_ed = [20e6, 40e6, 40e6]
    m_cr = [36.91e6, 36.91e6, 36.91e6]
    Inn_1 = [1_514_424_394] * 3
    Inn_2 = [978_984_614] * 3
    ECM = 32_836
    XI_MAX = 1965
    LOAD = 40
    SPAN_LENGHT = 4_960
    BETA = 0.5

    for i in range(len(xi_coords) - 1):
        print("\n", i)
        delta = deformazione(
            m_ed=m_ed[i],
            m_cr=m_cr[i],
            xi_a=xi_coords[i],
            xi_b=xi_coords[i + 1],
            xi_max=XI_MAX,
            Q=LOAD,
            L=SPAN_LENGHT,
            Inn_1=Inn_1[i],
            Inn_2=Inn_2[i],
            Ecm=ECM,
            beta=BETA,
        )
        print(delta)


def main_sec():
    cls = create_concrete_material("EC2", "C25/30")
    steel = create_steel_material("NTC18", "B450C")

    sec = ReinforcedConcreteSection(
        b=300,
        d=460,
        d1=40,
        d2=40,
        concrete_material=cls,
        As=Bars(n_bars=4, diameter=18, steel_material=steel),
        As1=Bars(n_bars=2, diameter=18, steel_material=steel),
        stirrups=Stirrups(n_braces=2, diameter=8, spacing=220, alpha=90),
        internal_forces=InternalForces(M=79.04 * 10 ** 6, N=0.0),
        name="C5_QP",
    )
    SECTIONS_LIST = [sec]
    XI_LIST = [0, 100]
    XI_MAX = 1965
    LOAD = 40
    SPAN_LENGHT = 4_960

    deflection_ReinforcedConcreteSection(
        list_of_sections=SECTIONS_LIST,
        list_of_xi_coords=XI_LIST,
        xi_max=XI_MAX,
        load=LOAD,
        span_lenght=SPAN_LENGHT,
        beta=0.5,
    )


# if __name__ == "__main__":
#   main_sec()

