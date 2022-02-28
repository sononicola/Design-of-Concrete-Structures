import json
from dataclasses import dataclass, field

GAMMA_C = 1.5
ALPHA_CC = 0.85
GAMMA_S = 1.15 


@dataclass()
class ConcreteMaterial:
    fck : int

    def __post_init__(self):
        self.fcd =  ALPHA_CC * self.fck/GAMMA_C
        self.fcm = self.fck + 8
        self.Ecm = 22000 * (self.fcm/10)**(0.3)
    
def create_concrete_section(code_name: str, concrete_type:str) -> ConcreteMaterial:
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
    #fff:float = field(default=self.fyk/1.5)

    def __post_init__(self):
        self.fyd = self.fyk/GAMMA_S
        self.Es = 210000
    
    
def create_steel_section(code_name: str, steel_type:str) -> ConcreteMaterial:
    """
    Create a SteelMaterial object using the database values as input
    code_name: "NTC18" or "EC2" 
    concrete_type: example: "B450C"
    """
    with open("reinforced concrete section/steel_database.json") as file:
        data = json.load(file)[code_name][steel_type]
        return SteelMaterial(**data) 
        
#############################################################################

c = create_concrete_section("NTC18","C25/30")
s = create_steel_section("NTC18","B450C")

print(c.Ecm)
print(s.fyd) 

