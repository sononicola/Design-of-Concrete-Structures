import json
from dataclasses import dataclass, field
from math import sqrt

GAMMA_C = 1.5
ALPHA_CC = 0.85
GAMMA_S = 1.15 


@dataclass()
class ConcreteMaterial:
    fck : float
    rck : float 
    fcm : float
    fcd : float
    Ecm : float
    fctm: float
    fctk: float
    fctd: float
    ec2 : float
    ecu2: float
    ec3 : float
    ecu3: float


    #def __post_init__(self):
        #self.fcd =  ALPHA_CC * self.fck/GAMMA_C
        #self.fcm = self.fck + 8
        #self.Ecm = 22000 * (self.fcm/10)**(0.3)
    
def create_concrete_material(code_name: str, concrete_type:str) -> ConcreteMaterial:
    """
    Create a ConcreteMaterial object using the database values as input
    code_name: "NTC18" or "EC2" 
    concrete_type: example: "C15/20"
    """
    with open("reinforced concrete section/concrete_database.json") as file:
        data = json.load(file)[code_name][concrete_type]
        return ConcreteMaterial(**data) 

#############################################################################

@dataclass()
class SteelMaterial:
    fyk : float
    Es : float
    #fff:float = field(default=self.fyk/1.5)

    def __post_init__(self):
        self.fyd = self.fyk/GAMMA_S
        self.ese = self.fyd/self.Es
    
    
def create_steel_material(code_name: str, steel_type:str) -> ConcreteMaterial:
    """
    Create a SteelMaterial object using the database values as input
    code_name: "NTC18" or "EC2" 
    concrete_type: example: "B450C"
    """
    with open("reinforced concrete section/steel_database.json") as file:
        data = json.load(file)[code_name][steel_type]
        return SteelMaterial(**data) 
        
#############################################################################

@dataclass()
class Geometry:
    b: int
    d: float
    d1: float = 0.
    As: float = 0.
    As1: float = 0.

    def __post_init__(self):
        self.h = self.d + self.d1

#TODO __print__ per includere il post init

def a(bars: int , diameter: int):
    return bars * 3.14 * diameter**2 / 4

c = create_concrete_material("EC2","C30/37")
s = create_steel_material("NTC18","B450C")

print(c)
print(s) 

b = Geometry(b=500., d=500., As=3200.)
#def SLE_As1(geeometry: Geometry, concrete: ConcreteMaterial, steel: SteelMaterial):
   # x = n * As / b * (-1 + sqrt(1+2*b*d/(n*As)))


def  SLE_As1_M(M, b, d, As, n=15):
    x = n * As / b * (-1 + sqrt(1+2*b*d/(n*As)))
    sigmac = 2 * M / (b*x*(d-x/3))
    sigmas = n * sigmac * (d - x) / x

    return sigmac, sigmas

#togliere le classi da qui e mettere solo variabili
def SLE_As1_M_NO(geometry: Geometry, concrete: ConcreteMaterial, steel: SteelMaterial, M):
    As = geometry.As
    d = geometry.d
    b = geometry.b

    x = n * As / b * (-1 + sqrt(1+2*b*d/(n*As)))
    sigmac = 2 * M / (b*x*(d-x/3))
    sigmas = n * sigmac * (d - x) / x

    return sigmac, sigmas

print(SLE_As1_M(
        b= b.b, 
        d=b.d,
        As = b.As,
        M=450000000))
