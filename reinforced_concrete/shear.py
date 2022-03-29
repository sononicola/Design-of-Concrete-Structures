from unittest import result
from sympy import sec
from reinforced_concrete.sections import ReinforcedConcreteSection

def shear_only_cls(d, bw, Asl, Ac, Ned, fck, gamma_c=1.5, alpha_cc=0.85) -> dict:
    """
    Corespond to Vrd on NTC18 and Vrd,c on EC2. 
    Shear resistence due to the only presence of CLS. If Ved<Vrd,c no specifiec armor is needed, but only the minimum.
    """
    k = min(1 + (200/d)**0.5, 2)
    nu_min = 0.035 * k**1.5 * fck**0.5
    rho_l = min(Asl/(bw*d) , 0.02)
    sigma_cp = min(Ned/Ac, 0.2 * fck*alpha_cc/gamma_c) # 0.2 * fcd  
    Vrd_1 = ((0.18*k*(100*rho_l*fck)**(1/3))/gamma_c + 0.15*sigma_cp)*bw*d
    Vrd_2 = nu_min + 0.15*sigma_cp*bw*d
    Vrd = max(Vrd_1, Vrd_2)

    results = {
        "k": k,
        "nu_min": nu_min,
        "rho_l": rho_l,
        "sigma_cp": sigma_cp,
        "Vrd_1": Vrd_1,
        "Vrd_2": Vrd_2,
        "Vrd": Vrd
    }
    return results

def shear(section: ReinforcedConcreteSection, gamma_c=1.5, alpha_cc=0.85):
    "layer"
    results = shear_only_cls(
            d = section.d,
            bw=section.b,
            Asl=section.As.area,
            Ac=section.b * section.h,
            Ned=section.internal_forces.N,
            fck=section.concrete_material.fck,
            gamma_c=gamma_c,
            alpha_cc=alpha_cc
        )
    #results[">Ved"] = results["Vrd"] > section.internal_forces.V
    return results
