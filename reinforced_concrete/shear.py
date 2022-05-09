from unittest import result
from reinforced_concrete.sections import ReinforcedConcreteSection
import numpy as np

# ---- NO SPECIFIC ARMOR, BUT ONLT THE MIN ----
def shear_only_cls(d, bw, Asl, Ac, Ned, fck, gamma_c=1.5, alpha_cc=0.85) -> dict:
    """
    Corespond to Vrd on NTC18 and Vrd,c on EC2. 
    Shear resistence due to the only presence of CLS. If Ved<Vrd,c no specific armor is needed, but only the minimum.
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

def shear_only_cls_layer(section: ReinforcedConcreteSection, gamma_c=1.5, alpha_cc=0.85):
    "layer. ipotesi che b=bw e A_s_long = As della sezione rettangolare"
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
    results[">Ved"] = results["Vrd"] > section.internal_forces.V
    return results

# ---- DESIGN OF SPECIFIC ARMOR ----
def design_theta(ved, d, bw, alpha, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> float:
    fcd = fck*alpha_cc/gamma_c
    fyd = fyk/gamma_s
    nu = 0.5 #resistenza di progetto a compressione ridotta del calcestruzzo d’anima
    return 1/2 * np.rad2deg(np.arcsin(2*ved/(nu*alpha_c*bw*0.9*d*fcd)))
def design_asw_min(n_braces, d_st) -> float:
    return n_braces * 3.1415 * d_st**2 / 4

def design_s(theta_ed, ved, n_braces, d_st, d, bw, alpha, fyk, gamma_s=1.15) -> float:
    asw_min = design_asw_min(n_braces=n_braces, d_st=d_st)
    fyd = fyk/gamma_s
    if ved == 0:
        return np.inf
    return 0.9*d*asw_min*fyd*(1/np.tan(np.deg2rad(theta_ed))) / ved

def design_specific_armor(ved, n_braces, d_st,d, bw, alpha, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> dict:
    results = {"ved": ved}
    theta_ed = design_theta(
        ved=ved, 
        d=d, 
        bw=bw, 
        alpha=alpha, 
        alpha_c=alpha_c, 
        fck=fck, 
        fyk=fck, 
        gamma_c=gamma_c, alpha_cc=alpha_cc, gamma_s=gamma_s)
    results["theta_ed"] = theta_ed

    theta_ed_real = max(theta_ed, 21.8)
    results["theta_ed_real"] = theta_ed_real

    s_ed = design_s(
        theta_ed = theta_ed_real, 
        ved=ved, 
        n_braces=n_braces,
        d_st=d_st,
        d=d, 
        bw=bw, 
        alpha=alpha, 
        fyk=fyk, 
        gamma_s=gamma_s)
    results["s_ed"] = s_ed
    return results

def design_specific_armor_layer(section: ReinforcedConcreteSection, alpha_c, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> dict:
    return design_specific_armor(
            ved=section.internal_forces.V, 
            n_braces=section.stirrups.n_braces, 
            d_st=section.stirrups.diameter,
            d=section.d, 
            bw=section.b, 
            alpha=section.stirrups.alpha,  
            alpha_c=alpha_c, 
            fck=section.concrete_material.fck, 
            fyk=section.As.steel_material.fyk, 
            gamma_c=gamma_c, 
            alpha_cc=alpha_cc, 
            gamma_s=gamma_s
            )


# ---- CHECK OF SPECIFIC ARMOR ----
def theta_r_calc(bw, Asw, alpha, s, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> float:
    """
    theta r calculated with Vr_cd == Vrsd
    alpha e theta in deg!

    """
    fcd = fck*alpha_cc/gamma_c
    fyd = fyk/gamma_s
    nu = 0.5 #resistenza di progetto a compressione ridotta del calcestruzzo d’anima

    cotg_theta = np.sqrt(-1 + alpha_c*bw*fcd*nu*s/(Asw*fyd*np.sin(np.deg2rad(alpha))))
    return np.rad2deg(np.arctan( 1/ cotg_theta)) # arc cotg theta

def calc_theta_r_real(theta_r_calculated: float) -> float:
    "Input a theta_r_calculated with theta_r_calc"
    if 21.8<theta_r_calculated<45:
        return theta_r_calculated
    elif theta_r_calculated>=45:
        return 45
    else:
        return 21.8

def calc_vrd(d, bw, Asw, alpha, theta, s, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> dict:
    """
    alpha e theta in deg!
    """
    nu = 0.5 #resistenza di progetto a compressione ridotta del calcestruzzo d’anima
    fcd = fck*alpha_cc/gamma_c
    fyd = fyk/gamma_s
    Vr_sd = 0.9*d*Asw/s * fyd * ((1/np.tan(np.deg2rad(alpha))) + (1/np.tan(np.deg2rad(theta)))) * (np.sin(np.deg2rad(alpha)))
    Vr_cd = 0.9*d*bw*alpha_c * nu * fcd * (((1/np.tan(np.deg2rad(alpha))) + (1/np.tan(np.deg2rad(theta)))))/(1+(1/np.tan(np.deg2rad(theta)))**2)
    Vr_d = min(Vr_sd, Vr_cd)

    results = {
        "Vr_sd": Vr_sd,
        "Vr_cd": Vr_cd,
        "Vr_d": Vr_d
    }
    return results

def shear_with_specific_armor(d, bw, Asw, alpha, s, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> dict:
    results = {}
    
    theta_calculated = theta_r_calc(
        bw=bw, 
        Asw=Asw, 
        alpha=alpha, 
        s=s, 
        alpha_c=alpha_c, 
        fck=fck, 
        fyk=fyk, 
        gamma_c=gamma_c, 
        alpha_cc=alpha_cc, 
        gamma_s=gamma_s
    )
    results["theta_calculated"] = theta_calculated

    theta_real = calc_theta_r_real(theta_calculated)
    results["theta_real"] = theta_real

    results.update(
        calc_vrd(
            d=d,
            bw=bw, 
            Asw=Asw, 
            alpha=alpha, 
            theta=theta_real,
            s=s, 
            alpha_c=alpha_c, 
            fck=fck, 
            fyk=fyk, 
            gamma_c=gamma_c, 
            alpha_cc=alpha_cc, 
            gamma_s=gamma_s
        )
    )
    return results

def shear_with_specific_armor_layer(section: ReinforcedConcreteSection, alpha_c, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15):
    results = shear_with_specific_armor(
            d=section.d, 
            bw=section.b, 
            Asw=section.stirrups.area, 
            alpha=section.stirrups.alpha,  
            s=section.stirrups.spacing, 
            alpha_c=alpha_c, 
            fck=section.concrete_material.fck, 
            fyk=section.As.steel_material.fyk, 
            gamma_c=gamma_c, 
            alpha_cc=alpha_cc, 
            gamma_s=gamma_s
            )
    results[">Ved"] = results["Vr_d"] > section.internal_forces.V
    return results