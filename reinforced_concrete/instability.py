from math import sqrt
from reinforced_concrete.sections import ReinforcedConcreteSection


def calc_eccentricity_0(l0: float) -> float:
    """
    e_0.
    l0: effective length
    """
    return max(l0 / 200, 20)


def calc_eccentricity_a(l0: float, theta_i: float = 1 / 200) -> float:
    """
    e_a.
    l0: effective length
    """
    return theta_i * l0 / 2


def calc_slenderness_ratio(l0: float, i: float) -> float:
    """
    l0: effective length
    i: radius of gyration of the uncracked concrete section = J/A
    i = b/sqrt(12) if pilar with b=h
    """
    return l0 / i


def calc_slenderness_ratio_limit_NTC18(Ned: float, Ac: float, fcd: float) -> float:
    "n = Ned/(Ac*fcd)"
    return 25 / sqrt(Ned / (Ac * fcd))


def is_stability_check_required(
    slenderness_ratio: float, slenderness_ratio_limit: float
) -> bool:
    return slenderness_ratio > slenderness_ratio_limit


def calc_phi_ef(phi_ef_oo, Me_QP, Me_ULS) -> float:
    """
    5.8.4 EC2
    
    phi_ef_oo da tab 11.2.VI delle NTC2018 o calcolandolo secondo quanto dice EC2 3.1.4
    """

    return phi_ef_oo * Me_QP / Me_ULS


def calc_e2_nominal_curvature_method(
    Ned, d, l0, Ac, As_tot, phi_ef, slenderness_ratio, fck, fcd, fyd, Es, c=10
) -> dict:
    """
    Calc the eccentricity of second order with the method from 5.8.8(3) EC2
    
    chi_0 == 1/r0 and chi == 1/r 
    c is a factor depending on the curvature distribution, see 5.8.8.2 (4) c=8-10
    """
    epsilon_yd = fyd / Es
    chi_0 = epsilon_yd / (0.45 * d)

    n = Ned / (Ac * fcd)
    omega = (As_tot * fyd) / (Ac * fcd)
    n_u = 1 + omega
    n_bal = 0.4
    k_r = (n_u - n) / (n_u - n_bal)

    beta = 0.35 + fck / 200 - slenderness_ratio / 150
    k_phi = max(1 + beta * phi_ef, 1)

    chi = k_r * k_phi * chi_0

    e2 = chi * l0 ** 2 / c

    return {
        "epsilon_yd": epsilon_yd,
        "chi_0": chi_0,
        "n": n,
        "omega": omega,
        "n_u": n_u,
        "n_bal": n_bal,
        "k_r": k_r,
        "beta": beta,
        "phi_ef": phi_ef,
        "k_phi": k_phi,
        "chi": chi,
        "e2": e2,
    }


def calc_bending_moment_nominal_curvature_method(
    Ned,
    d,
    l0,
    i,
    theta_i,
    Ac,
    As_tot,
    phi_ef_oo,
    Me_QP,
    Me_ULS,
    fck,
    fcd,
    fyd,
    Es,
    c=10,
) -> dict:

    slenderness_ratio = calc_slenderness_ratio(l0=l0, i=i)
    slenderness_ratio_limit = calc_slenderness_ratio_limit_NTC18(
        Ned=Ned, Ac=Ac, fcd=fcd
    )
    check_required: bool = is_stability_check_required(
        slenderness_ratio, slenderness_ratio_limit
    )

    if check_required == False:
        return {
            "slenderness_ratio": slenderness_ratio,
            "slenderness_ratio_limit": slenderness_ratio_limit,
            "check_required": check_required,
        }
    e0 = calc_eccentricity_0(l0=l0)
    ea = calc_eccentricity_a(l0=l0, theta_i=theta_i)

    phi_ef = calc_phi_ef(phi_ef_oo=phi_ef_oo, Me_QP=Me_QP, Me_ULS=Me_ULS)
    print(phi_ef)
    dict_e2 = calc_e2_nominal_curvature_method(
        Ned=Ned,
        d=d,
        l0=l0,
        Ac=Ac,
        As_tot=As_tot,
        phi_ef=phi_ef,
        slenderness_ratio=slenderness_ratio,
        fck=fck,
        fcd=fcd,
        fyd=fyd,
        Es=Es,
        c=c,
    )

    results = {
        "slenderness_ratio": slenderness_ratio,
        "slenderness_ratio_limit": slenderness_ratio_limit,
        "check_required": check_required,
        "e0": e0,
        "ea": ea,
    }
    results.update(dict_e2)
    results["e_tot"] = e0 + ea + dict_e2["e2"]
    results["Med"] = results["e_tot"] * Ned
    return results
