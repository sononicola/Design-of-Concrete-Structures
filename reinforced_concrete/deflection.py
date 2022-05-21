from modulefinder import LOAD_CONST
import sympy as sp
from scipy.integrate import quad

def zeta(m_cr:float, m_Q:sp.Function, beta:float) -> sp.Function:
    return 1 - beta*(m_cr/m_Q)**2

def chi(m_cr:float, m_Q:sp.Function, Inn_1:float, c:float, Ecm:float, beta:float) -> sp.Function:
    "c: Inn_2/Inn_1. c=1 se non fessurata e quindi rimane solo chi_1"
    chi_1 = m_Q/(Ecm*Inn_1)
    return chi_1 if c==1 else chi_1 * (1 + zeta(m_cr=m_cr, m_Q=m_Q, beta=beta)*(c-1))

def calc_c(m_ed:float, m_cr:float, Inn_1:float, Inn_2:float) -> float:
    return 1 if m_ed <= m_cr else Inn_1/Inn_2

def deformazione(m_ed:float, m_cr:float, xi_a:float, xi_b:float, xi_max:float, Q:float, L:float, Inn_1:float, Inn_2:float, Ecm:float, beta:float):
    xi = sp.symbols('xi')
    
    R_sx = (L - xi_max)/L 
    R_dx = xi_max/L
    M_sx = -R_sx*xi
    M_dx = -R_sx * xi + (xi-xi_max)
    if (xi_a<=xi_max and xi_b<=xi_max):
        m_F = M_sx
        print("M_sx")
    elif (xi_a>=xi_max and xi_b>=xi_max) :
        m_F = M_dx
        print("M_dx")
    elif (xi_a<xi_max) and (xi_b>xi_max):
        raise ValueError(f"i due estremi di integrazione devono stare o entrambi a sinistra o entrambi a destra di xi_max {xi_a = }, {xi_max = }, {xi_b = }")
    print(f"{m_F = }")
    
    m_Q = Q*(L*xi/2 - xi**2/2)
    print(f"{m_Q = }")

    c = calc_c(m_ed=m_ed, m_cr=m_cr, Inn_1=Inn_1, Inn_2=Inn_2)
    print(f"{c = }")

    chi_vera = chi(m_cr=m_cr, m_Q=m_Q, Inn_1=Inn_1, c=c, Ecm=Ecm, beta=beta)
    print(f"{chi_vera = }")
    
    #return sp.integrate(chi_vera*m_F, (xi, xi_a, xi_b))
    return quad(sp.lambdify(xi, chi_vera*m_F), xi_a, xi_b)[0]


delta = deformazione(m_ed=40e6, m_cr=36.91e6, xi_a=798, xi_b=1965, xi_max=1965, Q=50, L=4_960, Inn_1=1_514_424_394, Inn_2=978_984_614, Ecm=32_836.57, beta=0.5)
print(f"{delta = }")

print("---")

delta = deformazione(m_ed=40e6, m_cr=36.91e6, xi_a=1965, xi_b=3133, xi_max=1965, Q=50, L=4_960, Inn_1=1_514_424_394, Inn_2=978_984_614, Ecm=32_836.57, beta=0.5)
print(f"{delta = }")

def main():
    xi_coords = [0,798,1965,3133]
    m_ed = [20e6, 40e6, 40e6]
    m_cr = [36.91e6, 36.91e6, 36.91e6]
    Inn_1 = [1_514_424_394]*3
    Inn_2 =  [978_984_614]*3
    ECM = 32_836
    XI_MAX = 1965
    LOAD = 40
    SPAN_LENGHT = 4_960
    BETA=0.5

    for i in range(len(xi_coords)-1):
        print("\n",i)
        delta = deformazione(m_ed=m_ed[i], m_cr=m_cr[i], xi_a=xi_coords[i], xi_b=xi_coords[i+1], xi_max=XI_MAX, Q=LOAD, L=SPAN_LENGHT, Inn_1=Inn_1[i], Inn_2=Inn_2[i], Ecm=ECM, beta=BETA)
        print(delta)

if __name__ == "__main__":
    main()        