import sympy as sp
from .sections import ConcreteMaterial, SteelMaterial


def eq_m_prog(b, sigma_c, sigma_s1, xi, d, psi, lamb, As1, d2):
    return b * psi * xi * d * sigma_c * (d - lamb * xi * d) + sigma_s1 * As1 * (d - d2)


def eq_n_prog(b, sigma_c, sigma_s, sigma_s1, xi, d, psi, As, As1):
    return b * psi * xi * d * sigma_c + sigma_s1 * As1 - As * sigma_s


def design_b_constrain(
    cls: ConcreteMaterial,
    steel: SteelMaterial,
    beta: float,
    b: float,
    Med: float,
    d2: float,
) -> tuple:
    xi_23 = cls.ecu2 / (cls.ecu2 + steel.esu)
    psi = 17 / 21
    lamb = 99 / 238  # lambda
    # print(f"{xi_23 = }")

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
    return sol_23_prog[As], sol_23_prog[d]
