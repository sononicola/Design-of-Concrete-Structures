import sympy as sp
from typing import List, Tuple
from reinforced_concrete.sections import ReinforcedConcreteSection

def eq_m_prog(b, sigma_c, sigma_s1, xi, d, psi ,lamb, As1, d2):
    return b * psi * xi*d * sigma_c * (d - lamb*xi*d)  + sigma_s1*As1* (d - d2) 
def eq_n_prog(b, sigma_c, sigma_s, sigma_s1, xi, d, psi, As, As1):
    return b * psi * xi*d * sigma_c + sigma_s1*As1 - As*sigma_s

def sigmas_or_fyd(Es, es, fyd):
    return min(fyd, abs(Es*es))

def psi_2(xi, ec2, esu):
    if xi < 1/6:
        return xi/(1-xi) * esu/(3 * ec2**2) * (3 * ec2 - xi/(1-xi) * esu)
    else:
        return 1 - ( ec2*(1-xi) ) / ( 3*esu*xi )

def lamb_2(xi,ec2, esu):
# only for n = 2 C<C50/60
    if xi == 0: #TODO perché si faceva ?
        return 0
    elif xi <= 1/6:
        return (4*ec2 - esu*xi/(1-xi)) / (4*(3*ec2 - esu*xi/(1-xi))) 
    else:
        return ( (6*esu**2 + 4*esu*ec2 +  ec2**2)*xi**2 - 2*ec2**2 * xi + ec2**2 - 4*esu*ec2*xi ) / ( 4*esu*xi*((3*esu+ec2)*xi - ec2 ))

def compute(Med, Ned, b, d, d1, d2, As, As1, fcd, fyd, fyd1, \
            Es=210_000, Es1=210_000, ec2=2*10**-3, ecu=3.5*10**-3, \
            ese=1.863*10**-3, esu=10*10**-3, ese1=1.863*10**-3, esu1=10*10**-3) -> Tuple[dict, str]:
    results = {}
    logs = "--- LOG --- \nIpotesi di campo 3, calcolo della retta limite 2-3"

    # HP RETTA campo 2-3
    xi_23 = ecu / (ecu + esu)
    xi_34 = ecu/(ecu + ese)
    d2_xi23 =  (ecu - ese1)/ecu * xi_23 * d
    logs += f"\n{xi_23 = :.5f}"

    if d2 < d2_xi23:
        logs += f"\nEsiste campo 2a, 2b, 3b perchè {d2 = :.2f} < {d2_xi23 = :.2f} mm"
    else:
        logs += f"\nEsiste campo 2a, 3a, 3b perchè {d2 = :.2f} > {d2_xi23 = :.2f} mm" 
    
    # QUESTA xi_3 e la xi_2 dopo OCCORRE VEDERE SE È SEMPRE VALIDA LA PROF O SE LA PROF L'HA SEMPLIFICATA ALTRIMENTI USARE IL SOLVE TODO
    psi = 17/21 
    xi_3 = (Ned + As*fyd - As1*fyd1) / (b * psi * fcd * d)
    logs += f"\n{xi_3 = :.5f}"

    if xi_3 < xi_23:
        logs += f"\nIpotesi di campo 3 errata! {xi_3 = :.5f} < {xi_23 = :.5f}"
        logs += f"\nRicalcolo con ipotesi di campo 2B: armature superiori snervate"
        xi_2b = 1/16 * (15*(As*fyd - As1*fyd1 + Ned) / (b * fcd * d) + 1)  #TODO
        logs += f"\n{xi_2b = :.5f}"

        es1 = esu*(xi_2b - d2/d) / (1-xi_2b)
        if es1 > ese1:
            "CAMPO 2B"
            logs += "\n!!!!!!!!!!!!!!verifica del ec da fare" #TODO
            logs += f"\nIpotesi armature superiori snervate ok! {es1 = :.5%} > di {ese1 = :.5%}" #TODO per mille sarebbe meglio
            ec = (esu * xi_2b)/(1-xi_2b)
            if ec<ec2:
                logs+="FORMULA SBAGLIATA DI PSI PER EC"
                logs += f"\n{ec= :.5%} {ec2= :.5%}"
            es=esu
            #ricalcolo della psi e lambda
            xi = xi_2b
            psi = psi_2(xi, ec2, esu)
            lamb = lamb_2(xi, ec2, esu)

            results["campo"] = "2B" 
            results["es1"] = es1
            results["ec"] = ec
            results["es"] = esu
            results["xi"] = xi_2b
            results["psi"] = psi
            results["lamb"] = lamb
            results["Nrd"] = eq_n_prog(b=b, sigma_c=fcd, sigma_s=sigmas_or_fyd(Es,es,fyd), sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi, As=As, As1=As1)
            results["Mrd"] = eq_m_prog(b=b, sigma_c=fcd, sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi ,lamb=lamb, As1=As1, d2=d2)
        else:
            "CAMPO 2A"
            logs += "\n!!!!!!!!!!!!!!verifica del ec da fare" #TODO
            logs += f"\nIpotesi armature superiori snervate errata! {es1 = :.5%} < {ese1 = :.5%}"
            logs += f"\nRicalcolo con ipotesi di campo 2A: armature superiori in campo elastico e con ipotesi ec2<ec<ecu"
            # simbolico:
            xi = sp.symbols('xi', positive=True)
            psi = (16*xi-1)/(15*xi) #TODO prendere la formula generica e girarla
            es1 = esu*(xi - d2/d) / (1-xi) 
            eq_trasl = eq_n_prog(b=b, sigma_c=fcd, sigma_s=fyd, sigma_s1=Es1*es1, xi=xi, d=d, psi=psi, As=As, As1=As1) - Ned
            solution = sp.solve(eq_trasl, xi, dict=True)
            logs += f"\nGIUSTO PER VERIFICA DEL SOLVE{solution}"
            xi_2a = float(solution[0][xi])
            ec = (esu * xi_2a)/(1-xi_2a)
            if ec > ec2 and ec<ecu:
                logs+=f"\nIpotesi sul calcestruzzo confermata! ec2<ec<ecu: {ec2 = :.5%} < {ec = :.5%} < {ecu = :.5%}"
                es = esu
                es1 = esu*(xi_2a - d2/d) / (1-xi_2a)
                logs += f"\n{xi_2a = :.5f}\n{es1 = :.5%}\n{ec = :.5%}"
                
                #ricalcolo della psi e lambda
                xi = xi_2a
                psi = psi_2(xi, ec2, esu)
                lamb = lamb_2(xi, ec2, esu)

                results["campo"] = "2A" 
                results["xi"] = xi
                results["es1"] = es1
                results["ec"] = ec
                results["es"] = es
                results["psi"] = psi
                results["lamb"] = lamb
                results["Nrd"] = eq_n_prog(b=b, sigma_c=fcd, sigma_s=sigmas_or_fyd(Es,es,fyd), sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi, As=As, As1=As1)
                results["Mrd"] = eq_m_prog(b=b, sigma_c=fcd, sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi ,lamb=lamb, As1=As1, d2=d2)
            elif ec < ec2:
                logs+=f"\nIpotesi sul calcestruzzo errata! ec<ec2: {ec = :.5%} < {ec2 = :.5%}"
                logs+=f"\nRicalcolo di xi con l'altra formula di psi"
                # simbolico:
                xi = sp.symbols('xi')
                psi = (-5*xi*(8*xi-3))/(3*(xi-1)**2) #TODO prendere la formula generica e girarla
                es1 = esu*(xi - d2/d) / (1-xi) 
                eq_trasl = eq_n_prog(b=b, sigma_c=fcd, sigma_s=fyd, sigma_s1=Es1*es1, xi=xi, d=d, psi=psi, As=As, As1=As1) - Ned
                solution = sp.nsolve(eq_trasl, xi, xi_2a, dict=True)
                logs += f"\nGIUSTO PER VERIFICA DEL SOLVE{solution}"
                xi_2a = float(solution[0][xi])
                ec = (esu * xi_2a)/(1-xi_2a)
                es = esu
                es1 = esu*(xi_2a - d2/d) / (1-xi_2a)
                logs += f"\n{xi_2a = :.5f}\n{es1 = :.5%}\n{ec = :.5%}"
                
                #ricalcolo della psi e lambda
                xi = xi_2a
                psi = psi_2(xi, ec2, esu)
                lamb = lamb_2(xi, ec2, esu)

                results["campo"] = "2A" 
                results["xi"] = xi
                results["es1"] = es1
                results["ec"] = ec
                results["es"] = es
                results["psi"] = psi
                results["lamb"] = lamb
                results["Nrd"] = eq_n_prog(b=b, sigma_c=fcd, sigma_s=sigmas_or_fyd(Es,es,fyd), sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi, As=As, As1=As1)
                results["Mrd"] = eq_m_prog(b=b, sigma_c=fcd, sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi ,lamb=lamb, As1=As1, d2=d2)
    elif xi_3 > xi_23 and xi_3 < xi_34:
        "CAMPO 3A 3B"
        logs += f"\nIpotesi di essere in campo 3 ok! {xi_3 = :.5f} > di {xi_23 = :.5f} e < {xi_34 = :.5f} \nVerifico se 3A o 3B" #TODO
        es1 = ecu/xi_3 * (xi_3 - d2/d)
        if es1 > ese1:
            "CAMPO 3B"
            logs += f"\nIpotesi armature superiori snervate ok! {es1 = :.5%} > di {ese1 = :.5%}"
            es=ecu/xi_3 * (1 - xi_3)
            psi = 17/21 
            lamb = 99/238 #lambda
            xi=xi_3
            results["campo"] = "3B" 
            results["es"] = es
            results["es1"] = es1
            results["ec"] = ecu
            results["xi"] = xi_3
            results["psi"] = psi
            results["lamb"] = lamb
            results["Nrd"] = eq_n_prog(b=b, sigma_c=fcd, sigma_s=sigmas_or_fyd(Es,es,fyd), sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi, As=As, As1=As1)
            results["Mrd"] = eq_m_prog(b=b, sigma_c=fcd, sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi ,lamb=lamb, As1=As1, d2=d2)
    
        else:
            "CAMPO 3A"
            logs += f"\nIpotesi armature superiori non corrette, sono in campo elastico: {es1 = :.5%} < {ese1 = :.5%}\n Devo ricalcolare ricalcolare la xi"

            xi = sp.symbols('xi', positive=True)
            psi = 17/21
            es1 = ecu/xi * (xi - d2/d)
            eq_trasl = eq_n_prog(b=b, sigma_c=fcd, sigma_s=fyd, sigma_s1=Es1*es1, xi=xi, d=d, psi=psi, As=As, As1=As1) - Ned
            xi_3a = sp.solve(eq_trasl, xi, dict=True)[0][xi]
            logs += f"\n{xi_3a = :.5f}, che è maggiore di {xi_3 = :5f}. CONTROLLARE AD OCCHIO"
            es1 = ecu/xi_3a * (xi_3a - d2/d)
            logs += f"\n{es1 = :.5%}, che è minore di {ese1 = :.5%} quindi ipotesi di 3A OK" 
            ec = (esu * xi_3a)/(1-xi_3a)
            logs += f"\n{ec = :.5%}" 
            es=ecu/xi_3a * (1 - xi_3a) 
            psi = 17/21 
            lamb = 99/238 #lambda
            xi=xi_3a

            results["campo"] = "3A" 
            results["es"] = es
            results["es1"] = es1
            results["ec"] = ecu
            results["xi"] = xi_3a
            results["psi"] = psi
            results["lamb"] = lamb
            results["Nrd"] = eq_n_prog(b=b, sigma_c=fcd, sigma_s=sigmas_or_fyd(Es,es,fyd), sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi, As=As, As1=As1)
            results["Mrd"] = eq_m_prog(b=b, sigma_c=fcd, sigma_s1=sigmas_or_fyd(Es1,es1,fyd1), xi=xi, d=d, psi=psi ,lamb=lamb, As1=As1, d2=d2)
    else:
        "CAMPO 4 IN POI"
        logs += f"\nOltre campo 3 {xi_3 = :.5f} > di {xi_34 = :.5f}" 
    #print(locals())
    return results, logs



def layer_object_to_values(section:ReinforcedConcreteSection): #TODO
    b = section.b
    As = section.As.area
    As1 = section.As1.area
    d = section.d
    d1 = section.d1
    d2 = section.d2

    fck = section.concrete_material.fck
    Ec = section.concrete_material.Ecm
    ec2 = section.concrete_material.ec2
    ecu = section.concrete_material.ecu2

    fyk = section.As.steel_material.fyk
    Es = section.As.steel_material.Es
    ese = section.As.steel_material.ese
    esu = section.As.steel_material.esu

    fyk1 = section.As1.steel_material.fyk
    ese1 = section.As1.steel_material.ese
    esu1 = section.As1.steel_material.esu

def computeVero(section:ReinforcedConcreteSection) -> Tuple[dict, str]: #TODO CAMBIARE I NOMI DELLE FUNZIONI
    "Layer: object -> compute function"
    return compute(
            Med=section.internal_forces.M,
            Ned=section.internal_forces.N,
            b=section.b,
            d=section.d,
            d1=section.d1,
            d2=section.d2,
            As=section.As.area,
            As1=section.As1.area,
            fcd=section.concrete_material.fcd, 
            fyd=section.As.steel_material.fyd, 
            fyd1=section.As1.steel_material.fyd,
            Es=section.As.steel_material.Es, 
            Es1=section.As1.steel_material.Es, 
            ec2=section.concrete_material.ec2,
            ecu=section.concrete_material.ecu2,
            ese=section.As.steel_material.ese,
            esu=section.As.steel_material.esu,
            ese1=section.As1.steel_material.ese,
            esu1=section.As1.steel_material.esu,
            # TODO METTERE TUTTI
        )


    


