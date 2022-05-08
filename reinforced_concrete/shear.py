from reinforced_concrete.sections import ReinforcedConcreteSection
import numpy as np

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

def theta_calc(bw, Asw, alpha, s, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15):
    """
    alpha e theta in deg!
    """
    fcd = fck*alpha_cc/gamma_c
    fyd = fyk/gamma_s
    nu = 0.5 #resistenza di progetto a compressione ridotta del calcestruzzo d’anima

    cotg_theta = np.sqrt(-1 + alpha_c*bw*fcd*nu*s/(Asw*fyd*np.sin(np.deg2rad(alpha))))
    return np.rad2deg(np.arctan( 1/ cotg_theta)) # arc cotg theta

def shear_with_specific_armor(d, bw, Asw, alpha, theta, s, alpha_c, fck, fyk, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15) -> dict:
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

def shear_with_specific_armor_layer(section: ReinforcedConcreteSection, alpha_c, gamma_c=1.5, alpha_cc=0.85, gamma_s=1.15):
    theta_calculated = theta_calc(
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
    results = {"theta_calculated": theta_calculated}

    if 21.8<theta_calculated<45:
        theta_real = theta_calculated
    elif theta_calculated>=45:
        theta_real=45
    else:
        theta_real=21.8
    results["theta_real"] = theta_real

    results.update(
        shear_with_specific_armor(
            d=section.d, 
            bw=section.b, 
            Asw=section.stirrups.area, 
            alpha=section.stirrups.alpha, 
            theta=theta_real, 
            s=section.stirrups.spacing, 
            alpha_c=alpha_c, 
            fck=section.concrete_material.fck, 
            fyk=section.As.steel_material.fyk, 
            gamma_c=gamma_c, 
            alpha_cc=alpha_cc, 
            gamma_s=gamma_s
            )
        )
    results[">Ved"] = results["Vr_d"] > section.internal_forces.V
    return results