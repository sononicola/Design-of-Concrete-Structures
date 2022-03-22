import sympy as sp
from reinforced_concrete.sections import create_concrete_material, create_steel_material, Bars, ReinforcedConcreteSection

def eq_m_prog(b, sigma_c, sigma_s1, xi, d, psi ,lamb, As1, d2):
    return b * psi * xi*d * sigma_c * (d - lamb*xi*d)  + sigma_s1*As1* (d - d2) 
def eq_n_prog(b, sigma_c, sigma_s, sigma_s1, xi, d, psi, As, As1):
    return b * psi * xi*d * sigma_c + sigma_s1*As1 - As*sigma_s

def compute(Med, Ned, b, d, d1, d2, As, As1, fcd, fyd, fyd1, Es=210_000, Es1=210_000, ec2=2*10**-3, ecu=3.5*10**-3, ese=1.863*10**-3, esu=10*10**-3, ese1=1.863*10**-3, esu1=10*10**-3):
    results = {}
    logs = ["--- LOG ---", "Ipotesi di campo 3, calcolo della retta limite 2-3"]

    # HP RETTA campo 2-3
    xi_23 = ecu / (ecu + esu)
    xi_34 = ecu/(ecu + ese)
    d2_xi23 =  (ecu - ese1)/ecu * xi_23 * d
    logs.append(f"{xi_23 = :.4f}")

    if d2 < d2_xi23:
        logs.append(f"Esiste campo 2a, 2b, 3b perchè {d2 = :.2f} < {d2_xi23 = :.2f} mm")
    else:
        print(f"Esiste campo 2a, 3a, 3b perchè {d2 = :.2f} > {d2_xi23 = :.2f} mm") 
    
    # QUESTA xi_3 e la xi_2 dopo OCCORRE VEDERE SE È SEMPRE VALIDA LA PROF O SE LA PROF L'HA SEMPLIFICATA ALTRIMENTI USARE IL SOLVE TODO
    psi = 17/21 
    xi_3 = (Ned + As*fyd - As1*fyd1) / (b * psi * fcd * d)
    logs.append(f"{xi_3 = :.4f}")

    if xi_3 < xi_23:
        logs.append(f"Ipotesi di campo 3 errata! {xi_3 = :.4f} < di = {xi_23 = :.4f}")
        logs.append("Ricalcolo con ipotesi di campo 2B: armature superiori snervate")
        xi_2b = 1/16 * (15*(As*fyd - As1*fyd1 + Ned) / (b * fcd * d) + 1)  #TODO
        logs.append(f"{xi_2b = :.4f}")

        es1 = esu*(xi_2b - d2/d) / (1-xi_2b)
        if es1 > ese1:
            "CAMPO 2B"
            logs.append("!!!!!!!!!!!!!!verifica del ec da fare") #TODO
            logs.append(f"Ipotesi armature superiori snervate ok! {es1 = :.4%} > di {ese1 = :.4%}") #TODO per mille sarebbe meglio
            ec = (esu * xi_2b)/(1-xi_2b)
            logs.append(f"{ec= :.4%}")
            results["campo"] = "2B" 
            results["es1"] = es1
            results["ec"] = ec
            results["es"] = esu
            results["xi"] = xi_2b
        else:
            "CAMPO 2A"
            logs.append("!!!!!!!!!!!!!!verifica del ec da fare") #TODO
            logs.append(f"Ipotesi armature superiori snervate errata! {es1 = :.4%} < di {ese1 = :.5%}")
            logs.append("Ricalcolo con ipotesi di campo 2A: armature superiori in campo elastico")
            # simbolico:
            xi = sp.symbols('xi', positive=True)
            psi = (16*xi-1)/(15*xi) #TODO prendere la formula generica e girarla
            es1 = esu*(xi - d2/d) / (1-xi) 
            eq_trasl = eq_n_prog(b=b, sigma_c=fcd, sigma_s=fyd, sigma_s1=Es1*es1, xi=xi, d=d, psi=psi, As=As, As1=As1) - Ned
            print("GIUSTO PER VERIFICA DEL SOLVE",sp.solve(eq_trasl, xi, dict=True))
            xi_2a = sp.solve(eq_trasl, xi, dict=True)[0][xi]
            
            logs.append(f"{xi_2a = :.4f}")
            es1 = esu*(xi_2a - d2/d) / (1-xi_2a)
            logs.append(f"{es1 = :.4%}") 
            ec = (esu * xi_2a)/(1-xi_2a)
            logs.append(f"{ec = :.4%}") 
            results["campo"] = "2B" #TODO O 2A??
            results["xi"] = xi_2a
            results["es1"] = es1
            results["ec"] = ec
            results["es"] = esu
    elif xi_3 > xi_23 and xi_3 < xi_34:
        "CAMPO 3A 3B"
        logs.append(f"Ipotesi di essere in campo 3 ok! {xi_3 = :.4f} > di {xi_23 = :.4f} e < di {xi_34 = :.4f} \nVerifico se 3A o 3B") #TODO
        es1 = ecu/xi_3 * (xi_3 - d2/d)
        if es1 > ese1:
            "CAMPO 3B"
            logs.append(f"Ipotesi armature superiori snervate ok! {es1 = :.4%} > di {ese1 = :.4%}")
            es=ecu/xi_3 * (1 - xi_3)
            results["campo"] = "3B" 
            results["es"] = es
            results["es1"] = es1
            results["ec"] = ecu
            results["xi"] = xi_3
        else:
            "CAMPO 3A"
            logs.append(f"Ipotesi armature superiori non corrette, sono in campo elastico: {es1 = :.4%} < di {ese1 = :.4%}\n Devo ricalcolare ricalcolare la xi")

            xi = sp.symbols('xi', positive=True)
            psi = 17/21
            es1 = ecu/xi * (xi - d2/d)
            eq_trasl = eq_n_prog(b=b, sigma_c=fcd, sigma_s=fyd, sigma_s1=Es1*es1, xi=xi, d=d, psi=psi, As=As, As1=As1) - Ned
            xi_3a = sp.solve(eq_trasl, xi, dict=True)[0][xi]
            logs.append(f"{xi_3a = :.4f}, che è maggiore di {xi_3 = :4f}. CONTROLLARE AD OCCHIO")
            es1 = ecu/xi_3a * (xi_3a - d2/d)
            logs.append(f"{es1 = :.4%}, che è minore di {ese1 = :.4%} quindi ipotesi di 3A OK") 
            ec = (esu * xi_3a)/(1-xi_3a)
            logs.append(f"{ec = :.4%}") 
            es=ecu/xi_3a * (1 - xi_3a) 

            results["campo"] = "3A" 
            results["es"] = es
            results["es1"] = es1
            results["ec"] = ecu
            results["xi"] = xi_3a

    #TODO campo 3a 3b
    else:
        "CAMPO 4 IN POI"
        logs.append(f"Oltre campo 3 {xi_3 = :.4f} > di {xi_34 = :.4f}") 
    

    results["logs"] = logs
    return results

    psi = 17/21 
    lamb = 99/238 #lambda

def layer_object_to_values(ReinforcedConcreteSection): #TODO
    b = ReinforcedConcreteSection.b
    As = ReinforcedConcreteSection.As.area()
    As1 = ReinforcedConcreteSection.As1.area()
    d = ReinforcedConcreteSection.d
    d1 = ReinforcedConcreteSection.d1
    d2 = ReinforcedConcreteSection.d2

    fck = ReinforcedConcreteSection.concrete_material.fck
    Ec = ReinforcedConcreteSection.concrete_material.Ecm
    ec2 = ReinforcedConcreteSection.concrete_material.ec2
    ecu = ReinforcedConcreteSection.concrete_material.ecu2

    fyk = ReinforcedConcreteSection.As.steel_material.fyk
    Es = ReinforcedConcreteSection.As.steel_material.Es
    ese = ReinforcedConcreteSection.As.steel_material.ese
    esu = ReinforcedConcreteSection.As.steel_material.esu

    fyk1 = ReinforcedConcreteSection.As1.steel_material.fyk
    ese1 = ReinforcedConcreteSection.As1.steel_material.ese
    esu1 = ReinforcedConcreteSection.As1.steel_material.esu

def computeVero(Med,Ned, ReinforcedConcreteSection) -> compute: #TODO CAMBIARE I NOMI DELLE FUNZIONI
    "Layer object -> compure function"
    return compute(
            Med=Med,
            Ned=Ned,
            b=ReinforcedConcreteSection.b,
            d=ReinforcedConcreteSection.d,
            d1=ReinforcedConcreteSection.d1,
            d2=ReinforcedConcreteSection.d2,
            As=ReinforcedConcreteSection.As.area(),
            As1=ReinforcedConcreteSection.As1.area(),
            fcd=ReinforcedConcreteSection.concrete_material.fcd, 
            ec2=ReinforcedConcreteSection.concrete_material.ec2,
            ecu=ReinforcedConcreteSection.concrete_material.ecu2,
            fyd=ReinforcedConcreteSection.As.steel_material.fyd, 
            Es=ReinforcedConcreteSection.As.steel_material.Es, 
            ese=ReinforcedConcreteSection.As.steel_material.ese,
            esu=ReinforcedConcreteSection.As.steel_material.esu,
            fyd1=ReinforcedConcreteSection.As1.steel_material.fyd,
            Es1=ReinforcedConcreteSection.As1.steel_material.Es, 
            ese1=ReinforcedConcreteSection.As1.steel_material.ese,
            esu1=ReinforcedConcreteSection.As1.steel_material.esu,
            # TODO METTERE TUTTI
        )


    

def main():
    cls  = create_concrete_material("EC2","C25/30") 
    steel  = create_steel_material("NTC18","B450C")
    As = Bars(n_bars=6, diameter=14, steel_material=steel)
    As1 = Bars(n_bars=3, diameter=12, steel_material=steel)
    section = ReinforcedConcreteSection(b=300, d=410, d1=40, d2=40, concrete_material=cls, As=As, As1=As1, name="sec1")

    results_dict = computeVero(Med=207.2*10**6, Ned=0, ReinforcedConcreteSection=section)

    print(section.__repr__())
    print(results_dict)
    for log in results_dict["logs"]:
        print(log)

main()
quit()

#res = compute(Med=140, Ned=0, b=300, d=410, d1=40, d2=40, As=1206, As1=339, fcd=14.170, fyd=391.3, fyd1=391.3)
res = compute(Med=88_000_000, Ned=-22_000, b=400, d=310, d1=40, d2=40, As=1005, As1=1005, fcd=14.170, fyd=391.3, fyd1=391.3, ese=1.955*10**-3,ese1=1.955*10**-3)
print(res)
for log in res["logs"]:
    print(log)




xi= sp.symbols('xi', positive=True)
eq_trasl = eq_n_prog(b.value, f_cd.value, f_yd.value, f_yd.value, xi, d_design.value, psi , As_design.value, As1_design.value)
xi_sol = sp.solve(eq_trasl, xi, dict=True)[0][xi] 

print(f"xi = {xi_sol:.4f} \nx = xi * d = {xi_sol * d_design.value:.4f}")

if xi_sol < xi_23:
    print(f"Ipotesi di campo 3 errata! xi < di xi_23 = {xi_23:.4f}")
else:
    print(f"Ipotesi ok") #TODO

"negli input M è sempre + e se non lo è metto + e considero una sezione ruotata, che alla fine giro"

"N ha sempre segno opposto"