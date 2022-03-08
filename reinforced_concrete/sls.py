import numpy as np

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
    return n*(As+As1)/b * (-1 + np.sqrt(1+ (2*b*(As1*d2 + As*d))/(n*(As + As1)**2)))

#def neutral_axis_MN()

def sigma_c(M, x, d, d2, b,n=15):
    return M*x / (1/2 * b*x**2 * (d-x/3) + n*As1*(x-d2)*(d-d2))

def sigma_s(sigma_c, x , d, n=15):
    return n * sigma_c * (d - x) / x

def sigma_s1(sigma_c, x, d2, n=15):
    return n * sigma_c * (x - d2) / x

# -------------------
# FUNZIONI PER LA VERIFICA COMPLETA SLS/SLE
# -------------------

def sls_M(M, As, As1, d, d2, b, sigma_cR, sigma_sR, sigma_sR1, n=15) -> dict:
    """
    Verifica di un elemento a flessione semplice
    Input: int/float or np.array
    Output: dict[float or np.array]
    """
    x = neutral_axis_M(As=As, As1=As1, d=d, d2=d2, b=b, n=n)
    sigmac = sigma_c(M=M, x=x, d=d, d2=d2, b=b, n=n)
    sigmas = sigma_s(sigma_c=sigmac, x=x , d=d, n=n)
    sigmas1 = sigma_s1(sigma_c=sigmac, x=x, d2=d2, n=n)

    dic = {
        "x":x, 
        "sigma_c":sigmac, 
        "sigma_s":sigmas, 
        "sigma_s1":sigmas1,
        "<sigma_cR":sigmac < sigma_cR,
        "<sigma_sR":sigmas < sigma_sR,
        "<sigma_sR1":sigmas1 < sigma_sR1
        }

    return dic

