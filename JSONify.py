class JSONify:
    def __init__(self, reactants, concentration, units, reactant_kind):
        self.reactants = reactants
        self.concentration = concentration
        self.units = units
        self.reactant_kind = reactant_kind

    def ReactantJsonifier (self):
        reactants = {
            "reactants":self.reactants,
            "concentrations":self.concentration,
            "units":self.units,
            "reactant_kind":self.reactant_kind
        }

        
        return reactants
        