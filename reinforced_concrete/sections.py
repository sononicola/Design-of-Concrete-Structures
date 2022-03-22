import json
from dataclasses import dataclass, field
from math import sqrt

GAMMA_C = 1.5
ALPHA_CC = 0.85
GAMMA_S = 1.15 

"""
EXAMPLE OF HOW TO USE IT

cls = create_concrete_material("EC2","C30/37")
steel = create_steel_material("NTC18","B450C")
As = Bars(n_bars=6, diameter=20, steel_material=steel)
As1 = Bars(n_bars=3, diameter=12, steel_material=steel)

section_1 = ReinforcedConcreteSection(b=300, d=410, d1=40, d2=40, concrete_material=cls, As=As, As1=As1, name="sec1")
print(cls)
print(steel)
print(As)
print(As.area())
print(section_1)
"""

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
    with open("reinforced_concrete/concrete_database.json") as file:
        data = json.load(file)[code_name][concrete_type]
        return ConcreteMaterial(**data) 

#############################################################################

@dataclass()
class SteelMaterial:
    #name: str #TODO AGGIUNGERLO AL DATABASE
    fyk : float
    Es : float
    esu: float
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
    with open("reinforced_concrete/steel_database.json") as file:
        data = json.load(file)[code_name][steel_type]
        return SteelMaterial(**data) 
        
#############################################################################
@dataclass
class Bars:
    n_bars: int
    diameter: int
    steel_material: SteelMaterial

    def area(self):
        "Area"
        return self.n_bars * 3.14 * self.diameter**2 / 4

    def __str__(self):
        "Return a string like:'2Ø4' "
        return f"{self.n_bars}Ø{self.diameter}"

@dataclass()
class ReinforcedConcreteSection:
    b: int
    d: float
    d1: float 
    d2: float 
    concrete_material: ConcreteMaterial
    As: Bars
    As1: Bars
    name: str = "Section name"

    def __post_init__(self):
        self.h = self.d + self.d1




