from reinforced_concrete.sections import create_concrete_material, create_steel_material, Bars, ReinforcedConcreteSection
from reinforced_concrete.ULS import computeVero

def main():
    """
    Negli input M è sempre + e se non lo è metto + e considero una sezione ruotata, che alla fine girerò.
    N ha segno opposto negli slu
    """
    cls  = create_concrete_material("EC2","C25/30") 
    steel  = create_steel_material("NTC18","B450C")
   
    As = Bars(n_bars=5, diameter=16, steel_material=steel)
    As1 = Bars(n_bars=5, diameter=16, steel_material=steel)
    section = ReinforcedConcreteSection(b=400, d=310, d1=40, d2=40, concrete_material=cls, As=As, As1=As1, name="sec1")
    results_dict, logs = computeVero(Med=207.2*10**6, Ned=-22*10**3, section=section)
    print(section)
    print(logs)
    print(results_dict)

   # print(section.__dict__)

if __name__ == "__main__":
    main()