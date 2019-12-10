"""
Static keys for easier implementation of EnzymeML. Every field of a file refers to an hexadecimal ID.
This key system is implemented to use the SBML format in other notations like json or SQL, while being
compatible with EnzymeML (XML) format.

TODO EDITING ELEMENTS AFTER CREATION
"""

"""
Unspecific keys for the elements
"""
# string | dict: {"heading": string, "text": string}
UNSPECIFIC_NOTE = "UNSPECIFIC_NOTE"


"""
Meta data of the whole Combine Archive
"""
# dict: {"family", "given"}
META_CREATOR_NAME = "META_CREATOR_NAME"
# string
META_CREATOR_EMAIL = "META_CREATOR_EMAIL"
# string
META_CREATOR_ORCID = "META_CREATOR_ORCID"

# string
META_ORG_NAME = "META_ORG_NAME"

# string
META_FILE_URL = "META_FILE_URL"


"""
Main file fields
"""
# string
MAIN_META_EXPERIMENT_NAME = "MAIN_META_EXPERIMENT_NAME"

# dict: {"family": string, "given": string, "email": string, "orcid": string, "org": string}
MAIN_META_CREATOR = "MAIN_META_CREATOR"

# libsbml.Date | None (for now)
MAIN_META_DATES_CREATE = "MAIN_META_DATES_CREATE"
# libsbml.Date | None (for now)
MAIN_META_DATES_MODIFY = "MAIN_META_DATES_MODIFY"


# Link to the file itself or in the Combine Archive
# uri
MAIN_META_MODEL_IS = "MAIN_META_MODEL_IS"
# Link to the methods of this experiment, where it is described
# uri
MAIN_META_MODEL_DESCRIBED = "MAIN_META_MODEL_DESCRIBED"

# Link to the biological description like paper
# uri
MAIN_META_BIOL_DESCRIBED = "MAIN_META_BIOL_DESCRIBED"


# dict: {"name": string, "units": list[dict: {"kind": id, "exponent": -1/1, "scale": int, "multiplier": float}]}
MAIN_UNIT = "MAIN_UNIT"
# uri | list [uri]
MAIN_UNIT_IS = "MAIN_UNIT_IS"

# dict: {"name": string, "dimensions": int, "size": float, "units": id, "constant": bool=True}
MAIN_COMPARTMENT = "MAIN_COMPARTMENT"
# uri | list [uri]
MAIN_COMPARTMENT_IS = "MAIN_COMPARTMENT_IS"


# dict: {"name": string, "compartment": id, "type": sbo, "constant": bool, "init_conc": float, "init_amount": float,
#        "units": id, "stdev": (float, sid), "boundary_conditions": bool}
# no type leads to SBO term interactor
MAIN_SPECIES = "MAIN_SPECIES"
# dict: {"is": uri | list[uri],
#        "smiles": string, "iupac": string, "inchi": string}
MAIN_SPECIES_SPECIES = "MAIN_SPECIES_SPECIES"
# dict: {"sequence": fasta, "is": uri | list[uri], "hasPart": uri | list[uri], "hasTaxon": uri, "encodedBy": uri,
#        "occursIn": uri | list[uri]}
MAIN_SPECIES_PROTEIN = "MAIN_SPECIES_PROTEIN"


# dict: {"name": string, "reversible": bool, "reactants": list[{"id": sid, "stochiometry": int, "constant": bool}],
#        "modifiers": list[{"id": sid, "stochiometry": int, "constant": bool}],
#        "products": list[{"id": sid, "stochiometry": int, "constant": bool}]}
MAIN_REACTION = "MAIN_REACTION"
# dict: {"id": sid, "stochiometry": int, "constant": bool} | list[{"id": sid, "stochiometry": int, "constant": bool}]
MAIN_REACTION_REACTANTS = "MAIN_REACTION_REACTANTS"
# dict: {"id": sid, "stochiometry": int, "constant": bool} | list[{"id": sid, "stochiometry": int, "constant": bool}]
MAIN_REACTION_MODIFIERS = "MAIN_REACTION_MODIFIERS"
# dict: {"id": sid, "stochiometry": int, "constant": bool} | list[{"id": sid, "stochiometry": int, "constant": bool}]
MAIN_REACTION_PRODUCTS = "MAIN_REACTION_PRODUCTS"
# string
MAIN_REACTION_EC_CODE = "MAIN_REACTION_EC_CODE"
# dict: {"ph": float, "temperature": (float, id), "pressure": (float, id), "shaking": (float, id)}
MAIN_REACTION_CONDITION = "MAIN_REACTION_CONDITION"
# EnzymeMLReplica | list[EnzymeMLReplica]
MAIN_REACTION_REPLICAS = "MAIN_REACTION_REPLICAS"
# EnzymeMLFormat
MAIN_DATA_FORMAT = "MAIN_DATA_FORMAT"
# dict: {"file": uri, "format": id}
MAIN_DATA_FILE = "MAIN_DATA_FILE"
# dict: {"name": string, "file": id, "start": int, "stop": int}
MAIN_DATA_MEASUREMENTS = "MAIN_DATA_MEASUREMENTS"

"""
Model file fields
"""
# string
MODEL_META_EXPERIMENT_NAME = "MODEL_META_EXPERIMENT_NAME"

# dict: {"family": string, "given": string, "email": string, "orcid": string, "org": string}
MODEL_META_CREATOR = "MODEL_META_CREATOR"

# libsbml.Date | None (for now)
MODEL_META_DATES_CREATE = "MODEL_META_DATES_CREATE"
# libsbml.Date | None (for now)
MODEL_META_DATES_MODIFY = "MODEL_META_DATES_MODIFY"


# Link to the file itself or in the Combine Archive
# uri
MODEL_META_MODEL_IS = "MODEL_META_MODEL_IS"
# Link to the methods of this experiment, where it is described
# uri
MODEL_META_MODEL_DESCRIBED = "MODEL_META_MODEL_DESCRIBED"
# dict: {"name": string, "type": sbo, "constant": bool}
# no type leads to SBO term interactor
MODEL_SPECIES = "MODEL_SPECIES"

# dict: {"name": string, "reversible": bool, "reactants": list[ReactionComponent],
#        "modifiers": list[{"id": sid, "stochiometry": int, "constant": bool}],
#        "products": list[ReactionComponent], "kineticlaw": string,
#        "parameters": list[{"name": string, "value": float, "units": id, "stdev": (float, id)}]}
MODEL_REACTION = "MODEL_REACTION"
# dict: {"id": sid, "stochiometry": int, "constant": bool} | list[{"id": sid, "stochiometry": int, "constant": bool}]
MODEL_REACTION_REACTANTS = "MODEL_REACTION_REACTANTS"
# dict: {"id": sid, "stochiometry": int, "constant": bool} | list[{"id": sid, "stochiometry": int, "constant": bool}]
MODEL_REACTION_MODIFIERS = "MODEL_REACTION_MODIFIERS"
# dict: {"id": sid, "stochiometry": int, "constant": bool} | list[{"id": sid, "stochiometry": int, "constant": bool}]
MODEL_REACTION_PRODUCTS = "MODEL_REACTION_PRODUCTS"
# The formula of the model as a simple string. Parameters are to be stated as SID or parameter.
# string
MODEL_REACTION_KINETIC_LAW = "MODEL_REACTION_KINETIC_LAW"
# dict: {"name": string, "value": float, "units": id, "stdev": (float, id)}
MODEL_REACTION_PARAMETERS = "MODEL_REACTION_PARAMETERS"
# dict: {sid: [sid]}
# reaction sid of experiment file as key, lists all sids of used replica ids
MODEL_REACTION_DATA = "MODEL_REACTION_DATA"
# TODO MIRIAM

MODEL_test = "MODEL_test"
