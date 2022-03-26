import numpy as np
import sympy as sp
from typing import Tuple
from reinforced_concrete.sections import ReinforcedConcreteSection

"RETTANGOLO"


"""
d1 : d primo,  
d2 : d secondo
_M : solo flessione, senza pressione N
_MN: pressoflessione
"""
# -------------------
# -- FUNZIONI BASE --
# -------------------

def neutral_axis_M(As, As1, d, d2, b, n=15):
    "When only bending moment is applied"
    return n*(As+As1)/b * (-1 + np.sqrt(1+ (2*b*(As1*d2 + As*d))/(n*(As + As1)**2)))

def sigma_c_M(M, As1, x, d, d2, b,n=15):
    "When only bending moment is applied"
    return M*x / (1/2 * b*x**2 * (d-x/3) + n*As1*(x-d2)*(d-d2))

def neutral_axis_MN(M, N, b, d, d1, d2, As, As1, n=15):
    d0 = M/N - (d+d1)/2
    x = sp.symbols('x')
    eq = 1/6*b*x**3 + 1/2*b*d0*x**2 + (n*As1*(d0+d2) + n*As*(d0+d))*x - n*As1*d2*(d0+d2) - n*As*d*(d0+d)
    sol = sp.nsolve(eq, x, d/2, dict=True)[0][x] #d/2 is the starting point 
    return sol

def sigma_c_MN(N, As, As1, x, d, d2, b, n=15):
    "When only bending moment is applied"
    return (N*x / (  1/2 *b *x**2 + n*As1*(x-d2) - n*As*(d-x)  ))

def sigma_s(sigma_c, x , d, n=15):
    return n * sigma_c * (d - x) / x

def sigma_s1(sigma_c, x, d2, n=15):
    return n * sigma_c * (x - d2) / x

# -------------------
# FUNZIONI PER LA VERIFICA COMPLETA SLS/SLE
# -------------------

#def sls_M(M, As, As1, d, d2, b, sigma_cR, sigma_sR, sigma_sR1, n=15) -> dict:
#    """
#    Verifica di un elemento a flessione semplice
#    Input: int/float or np.array
#    Output: dict[float or np.array]
#    """
#    x = neutral_axis_M(As=As, As1=As1, d=d, d2=d2, b=b, n=n)
#    sigmac = sigma_c_M(M=M, As1=As1, x=x, d=d, d2=d2, b=b, n=n)
#    sigmas = sigma_s(sigma_c=sigmac, x=x , d=d, n=n)
#    sigmas1 = sigma_s1(sigma_c=sigmac, x=x, d2=d2, n=n)
#
#    dic = {
#        "x":x, 
#        "sigma_c":sigmac, 
#        "sigma_s":sigmas, 
#        "sigma_s1":sigmas1,
#        "<sigma_cR":sigmac < sigma_cR,
#        "<sigma_sR":sigmas < sigma_sR,
#        "<sigma_sR1":sigmas1 < sigma_sR1
#        }
#
#    return dic
#
#def sls_MN(M, N, As, As1, d, d1, d2, b, sigma_cR, sigma_sR, sigma_sR1, n=15) -> dict:
#    """
#    Verifica di un elemento a flessione semplice
#    Input: int/float or np.array
#    Output: dict[float or np.array]
#    """
#    x = neutral_axis_MN(M=M, N=N, b=b, d=d, d1=d1, d2=d2, As=As, As1=As1, n=n)
#    sigmac = sigma_c_MN(N=N, As=As, As1=As1, x=x, d=d, d2=d2, b=b, n=n)
#    sigmas = sigma_s(sigma_c=sigmac, x=x , d=d, n=n)
#    sigmas1 = sigma_s1(sigma_c=sigmac, x=x, d2=d2, n=n)
#
#    dic = {
#        "x":x, 
#        "sigma_c":sigmac, 
#        "sigma_s":sigmas, 
#        "sigma_s1":sigmas1,
#        "<sigma_cR":sigmac < sigma_cR,
#        "<sigma_sR":sigmas < sigma_sR,
#        "<sigma_sR1":sigmas1 < sigma_sR1
#        }
#
#    return dic

def sls_entrambe_temp(M, N, As, As1, d, d1, d2, b, sigma_cR, sigma_sR, sigma_sR1, n=15) -> Tuple[dict, str]:
    """
    N positivo compressione !
    """
    logs = ""
    if N == 0:
        logs += "Flessione semplice"
        x = neutral_axis_M(As=As, As1=As1, d=d, d2=d2, b=b, n=n)
        sigmac = sigma_c_M(M=M, As1=As1, x=x, d=d, d2=d2, b=b, n=n)
    elif N>0:
        logs += "Presso-flessione"
        x = neutral_axis_MN(M=M, N=N, b=b, d=d, d1=d1, d2=d2, As=As, As1=As1, n=n)
        sigmac = sigma_c_MN(N=N, As=As, As1=As1, x=x, d=d, d2=d2, b=b, n=n)
    else:
        logs += "Tenso-flessione"
        #TODO
    sigmas = sigma_s(sigma_c=sigmac, x=x , d=d, n=n)
    sigmas1 = sigma_s1(sigma_c=sigmac, x=x, d2=d2, n=n)

    dic = {
        "x": float(x), 
        "sigma_c": float(sigmac), 
        "sigma_s": float(sigmas), 
        "sigma_s1": float(sigmas1),
        "<sigma_cR":sigmac < sigma_cR,
        "<sigma_sR":sigmas < sigma_sR,
        "<sigma_sR1":sigmas1 < sigma_sR1
        }

    return dic, logs

def sls(section:ReinforcedConcreteSection, n=15) -> Tuple[dict, str]: #TODO CAMBIARE I NOMI DELLE FUNZIONI
    "Layer: object -> sls_entrambe_temp"
    return sls_entrambe_temp(
            M=section.internal_forces.M,
            N=section.internal_forces.N,
            b=section.b,
            d=section.d,
            d1=section.d1,
            d2=section.d2,
            As=section.As.area,
            As1=section.As1.area,
            sigma_cR=section.concrete_material.sigmac,
            sigma_sR=section.As.steel_material.sigmar,
            sigma_sR1=section.As1.steel_material.sigmar,
            n=n
        )
