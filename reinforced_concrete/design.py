import sympy as sp
from .sections import ConcreteMaterial, SteelMaterial
from .ULS import psi_2, lamb_2

import numpy.testing as npt


def eq_m_prog(b, sigma_c, sigma_s1, xi, d, psi, lamb, As1, d2):
    return b * psi * xi * d * sigma_c * (d - lamb * xi * d) + sigma_s1 * As1 * (d - d2)


def eq_n_prog(b, sigma_c, sigma_s, sigma_s1, xi, d, psi, As, As1):
    return b * psi * xi * d * sigma_c + sigma_s1 * As1 - As * sigma_s


def rect_b_constrain_M(
    cls: ConcreteMaterial,
    steel: SteelMaterial,
    beta: float,
    b: float,
    Med: float,
    d2: float,
) -> dict:
    "rectangular section with b and beta fixed, and with only M applied. As and d have to be found "
    xi_23 = cls.ecu2 / (cls.ecu2 + steel.esu)
    psi = 17 / 21
    lamb = 99 / 238  # lambda

    As, d = sp.symbols("As, d", positive=True)
    eq_m23 = eq_m_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s1=steel.fyd,
        xi=xi_23,
        d=d,
        psi=psi,
        lamb=lamb,
        As1=beta * As,
        d2=d2,
    )
    eq_n23 = eq_n_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s=steel.fyd,
        sigma_s1=steel.fyd,
        xi=xi_23,
        d=d,
        psi=psi,
        As=As,
        As1=beta * As,
    )
    sol_23_prog = sp.solve((eq_m23 - Med, eq_n23), As, d, dict=True)[0]
    return {
        "xi_23": xi_23,
        "As": float(sol_23_prog[As]),
        "As1": float(sol_23_prog[As] * beta),
        "d": float(sol_23_prog[d]),
    }


def rect_d_constrain_M(
    cls: ConcreteMaterial,
    steel: SteelMaterial,
    beta: float,
    d: float,
    Med: float,
    d2: float,
) -> dict:
    "rectangular section with d and beta fixed, and with only M applied. As and b have to be found "
    xi_23 = cls.ecu2 / (cls.ecu2 + steel.esu)
    psi = 17 / 21
    lamb = 99 / 238  # lambda

    As, b = sp.symbols("As, b", positive=True)
    eq_m23 = eq_m_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s1=steel.fyd,
        xi=xi_23,
        d=d,
        psi=psi,
        lamb=lamb,
        As1=beta * As,
        d2=d2,
    )
    eq_n23 = eq_n_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s=steel.fyd,
        sigma_s1=steel.fyd,
        xi=xi_23,
        d=d,
        psi=psi,
        As=As,
        As1=beta * As,
    )
    sol_23_prog = sp.solve((eq_m23 - Med, eq_n23), As, b, dict=True)[0]
    return {
        "xi_23": xi_23,
        "As": float(sol_23_prog[As]),
        "As1": float(sol_23_prog[As] * beta),
        "b": float(sol_23_prog[b]),
    }


def T_inverted_M(
    cls: ConcreteMaterial, steel: SteelMaterial, b: float, d: float, Med: float
) -> dict:
    """T inverted section b and d fixed, and with only M applied. 
    b is the lower base.
    As and xi have to be found """

    psi = 17 / 21
    lamb = 99 / 238  # lambda

    As, xi = sp.symbols("As, xi", positive=True)
    eq_m23 = eq_m_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s1=steel.fyd,
        xi=xi,
        d=d,
        psi=psi,
        lamb=lamb,
        As1=0,  # there is no As1 area in T sections
        d2=0,
    )
    eq_n23 = eq_n_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s=steel.fyd,
        sigma_s1=steel.fyd,
        xi=xi,
        d=d,
        psi=psi,
        As=As,
        As1=0,  # there is no As1 area in T sections
    )
    sol_3_prog = sp.solve((eq_m23 - abs(Med), eq_n23), As, xi, dict=True)[0]
    return {"xi": float(sol_3_prog[xi]), "As": float(sol_3_prog[As])}


def T_straight_M(cls, steel, b: float, d: float, Med: float) -> dict:
    """T section b and d fixed, and with only M applied. 
    b is the upper base.
    As and xi have to be found """

    As, xi = sp.symbols("As, xi")

    ec2 = cls.ec2
    esu = steel.esu
    psi = xi / (1 - xi) * esu / (3 * ec2 ** 2) * (3 * ec2 - xi / (1 - xi) * esu)
    lamb = (4 * ec2 - esu * xi / (1 - xi)) / (4 * (3 * ec2 - esu * xi / (1 - xi)))

    eq_m23 = eq_m_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s1=steel.fyd,
        xi=xi,
        d=d,
        psi=psi,
        lamb=lamb,
        As1=0,  # there is no As1 area in T sections
        d2=0,
    )
    eq_n23 = eq_n_prog(
        b=b,
        sigma_c=cls.fcd,
        sigma_s=steel.fyd,
        sigma_s1=steel.fyd,
        xi=xi,
        d=d,
        psi=psi,
        As=As,
        As1=0,  # there is no As1 area in T sections
    )

    # Due to sympy bugs, I'm calculating xi with two different methods and checking then if they are (almost) equals
    xi_sympy = sp.re(sp.solve(eq_m23 - abs(Med), xi)[1])
    sol_2A_prog = sp.nsolve(
        (eq_m23 - abs(Med), eq_n23), (xi, As), (0.1, 200), dict=True
    )[0]
    npt.assert_almost_equal(float(xi_sympy), float(sol_2A_prog[xi]), decimal=5)
    return {"xi": float(sol_2A_prog[xi]), "As": float(sol_2A_prog[As])}


def possible_areas(minimum_area: float, diams: list = [12, 14, 16, 18, 20, 22]) -> str:
    string = []
    for diam in diams:
        n = 1 + int(minimum_area / (3.14 * diam ** 2 / 4))
        string.append(f"{n:>2}Ø{diam} = {n * 3.14 * diam**2 / 4:.2f} mm2  \n")

    return "".join(string)
