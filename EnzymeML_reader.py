from __future__ import print_function
from flask import Flask, render_template, request, url_for, jsonify
import matplotlib.pyplot as plt
from libsbml import *
import seaborn as sns
import pandas as pd
import numpy as np
import os
from EnzymeML import EnzymeMLwriter
import numpy as np
import json
from libcombine import *
import sys


class CombineArchiveExtractor():
    def __init__(self, archive_path, enzymeML_path ):
        self.archive_path = archive_path
        self.enzymeML_path = enzymeML_path

    def extractEnzymeMLFile (self):
        archive = CombineArchive()
        archive.initializeFromArchive(self.archive_path)
        document = readSBMLFromString(archive.extractEntryToString(self.enzymeML_path))
        model = document.getModel()
        return model

    def readModel (self):

        model = self.extractEnzymeMLFile()
        
        substrates = []
        SBOterm = []

        for i in range (model.getNumSpecies()):
            substrates.append(model.getSpecies(i).getName())
            
            SBOterm.append(model.getSpecies(i).getSBOTerm())
            


        print(model.getNumSpecies())
        print(substrates)
        print(SBOterm)
        


        print("das Modell ist")
        




combine_archive_path = "2019 12 09 00,00,00AHAS Reaction_awe.omex"

new_EnzymeML = CombineArchiveExtractor(combine_archive_path, "./experiment.xml")
new_EnzymeML.readModel()

    



    
    





archive = CombineArchive()
archive.initializeFromArchive("2019 12 09 00,00,00AHAS Reaction_awe.omex")
print(archive.getNumEntries())

for i in range(2):
    entry = archive.getEntry(i)
    print(entry.getLocation())

experiment = archive.getEntry(0)
print("location")
print(experiment)
print(experiment.getLocation())

document = archive.extractEntryToString(experiment.getLocation())

SBML = readSBMLFromString(document)
model = SBML.getModel()
print(model)
print(SBML)


units = []
print(units)

for i in range(model.getNumUnitDefinitions()):
    units.append(model.getUnitDefinition(i))

print(units)


#print("Die Anzahl der Einheiten ist:" + units)



