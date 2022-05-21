import json
from dataclasses import dataclass, field
from math import sqrt

GAMMA_C = 1.5
ALPHA_CC = 0.85
GAMMA_S = 1.15 

"""
EXAMPLE OF HOW TO USE IT

cls  = create_concrete_material("EC2","C25/30", is_sls_qp=False) 
steel  = create_steel_material("NTC18","B450C")
As = Bars(n_bars=5, diameter=16, steel_material=steel)
As1 = Bars(n_bars=5, diameter=16, steel_material=steel)
forces = InternalForces(M=207.2*10**6, N=-22*10**3)
section = ReinforcedConcreteSection(b=400, d=310, d1=40, d2=40, concrete_material=cls, As=As, As1=As1, internal_forces=forces, name="sec1")

print(cls.__repr__())
print(steel.__repr__())
print(As.__str__())
print(As.__repr__())
print(As.area)
print(section)
print(section.__repr__())
print(section.to_dict())

custom_cls = ConcreteMaterial(bla bla bla)
"""

@dataclass()
class ConcreteMaterial:
    "is_sls_qp: if True is used to set sigmaCr to the quasi-permanently with is 0.45 fck. Default is False, so sigmaCr is 0.6 fck"
    name : str
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
    is_sls_qp: bool = False

    @property
    def sigmac(self):
        return 0.45 * self.fck if self.is_sls_qp else 0.6 * self.fck #TODO rename in sigmar
    
def create_concrete_material(code_name: str, concrete_type:str, is_sls_qp=False) -> ConcreteMaterial:
    """
    Create a ConcreteMaterial object using the database values as input
    code_name: "NTC18" or "EC2" 
    concrete_type: example: "C15/20"
    is_sls_qp: if True is used to set sigmaCr to the quasi-permanently with is 0.45 fck. Default is False, so sigmaCr is 0.6 fck
    
    """
    with open("reinforced_concrete/concrete_database.json") as file:
        data = json.load(file)[code_name][concrete_type]
        data["is_sls_qp"] =  is_sls_qp  
        return ConcreteMaterial(**data) 

#############################################################################

@dataclass()
class SteelMaterial:
    name: str 
    fyk : float
    Es : float
    esu: float
    #fff:float = field(default=self.fyk/1.5)

    def __post_init__(self):
        self.fyd = self.fyk/GAMMA_S
        self.ese = self.fyd/self.Es
        self. sigmar = 0.8 * self.fyk
    
    
def create_steel_material(code_name: str, steel_type:str) -> SteelMaterial:
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
    steel_material: SteelMaterial = create_steel_material("NTC18","B450C")

    def __post_init__(self):
        self.area = self.n_bars * 3.1415 * self.diameter**2 / 4

    def __str__(self):
        "Return a string like:'2Ø4' "
        return f"{self.n_bars}Ø{self.diameter}"

@dataclass
class Stirrups:
    n_braces: int 
    diameter: int 
    spacing: int 
    alpha: int = 90
    steel_material: SteelMaterial = create_steel_material("NTC18","B450C")

    def __post_init__(self):
        self.area = self.n_braces * 3.1415 * self.diameter**2 / 4

    def __str__(self):
        "Return a string like:'2Ø8/200' "
        return f"{self.n_braces}Ø{self.diameter}/{self.spacing}"

@dataclass()
class InternalForces:
    M: float = 0.
    N: float = 0.
    V: float = 0.
    
@dataclass()
class ReinforcedConcreteSection:
    b: int
    d: float
    d1: float 
    d2: float 
    concrete_material: ConcreteMaterial
    As: Bars
    As1: Bars
    internal_forces: InternalForces
    stirrups: Stirrups = None
    name: str = "no name assigned"

    def __post_init__(self):
        self.h = self.d + self.d1

    def Inn_1(self, n=15, n1=1) -> float:
        """
        Return the moment of inertia when CLS is in state 1, so the CLS tension strenght is considered. Only bending moment applied.
        n = Es/Ec. Default = 15
        n1 = Ec_tension/Ec_compression. Default = 1
        """
        x = (n*(self.As.area*self.d + self.As1.area*self.d2) + self.b*self.h**2/2)/(n*(self.As.area + self.As1.area) + self.b*self.h)
        return self.b*x**3/3 + n*self.As1.area*(x-self.d2)**2 + n1*self.b*(self.h-x)**3/3 + n*self.As.area*(self.d-x)**2
    
    def __str__(self):
        "Return a beautiful printed string with all usefull properties "
        return f"""
Section name: {self.name}
{'':3}{'CLS ':>4}= {self.concrete_material.name}
{'':3}{'B ':>4}= {self.b} mm
{'':3}{'H ':>4}= {self.h} mm
{'':3}{'d ':>4}= {self.d} mm
{'':3}{'d1 ':>4}= {self.d1} mm
{'':3}{'d2 ':>4}= {self.d2} mm
{'':3}{'As ':>4}= {self.As.__str__():>5} = {self.As.area:>5.0f} mm2 | {self.As.steel_material.name}
{'':3}{'As1 ':>4}= {self.As1.__str__():>5} = {self.As1.area:>5.0f} mm2 | {self.As1.steel_material.name}
{'':3}{'Med ':>4}= {self.internal_forces.M} Nmm
{'':3}{'Ned ':>4}= {self.internal_forces.N} N
{'':3}{'Ved ':>4}= {self.internal_forces.V} N
"""

    def to_dict(self):
        "Return a dictionary with all usefull properties. If want all values use asdict(object) after have imported it "
        return {
                    "name": self.name,
                    "CLS": self.concrete_material.name,
                    "Steel": self.As.steel_material.name,
                    "Steel1": self.As1.steel_material.name,
                    "B": self.b,
                    "H": self.h,
                    "d":self.d,
                    "d1": self.d1,
                    "d2": self.d2,
                    "As_str": self.As.__str__(),
                    "As_area" : self.As.area,
                    "As1_str": self.As1.__str__() ,
                    "As1_area" : self.As1.area,
                    "Ast_str" : self.stirrups.__str__(),
                    "Med": self.internal_forces.M,
                    "Ned": self.internal_forces.N,
                    "Ved":self.internal_forces.V
                }