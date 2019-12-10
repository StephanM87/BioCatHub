import libsbml as sbml

doc = sbml.SBMLDocument(3, 2)
model = doc.createModel()
model.setMetaId("META_MODEL")

cvt = sbml.CVTerm()
cvt.setQualifierType(sbml.BIOLOGICAL_QUALIFIER)
cvt.setBiologicalQualifierType(sbml.BQB_IS)
cvt.addResource("www.some.reference.de/bug/annotation")

print(sbml.writeSBMLToString(doc))

model.addCVTerm(cvt)
print(sbml.writeSBMLToString(doc))

model.unsetAnnotation()

ann = "<test><other/></test>"
model.appendAnnotation(ann)
print(sbml.writeSBMLToString(doc))

model.unsetAnnotation()
model.appendAnnotation(ann)
model.addCVTerm(cvt)
print(sbml.writeSBMLToString(doc))

model.unsetAnnotation()
model.addCVTerm(cvt)
print(sbml.writeSBMLToString(doc))
model.appendAnnotation(ann)
print(sbml.writeSBMLToString(doc))

# Here the bug occurs: The CVTerm gets deleted by the appendAnnotation
model.unsetAnnotation()
model.addCVTerm(cvt)
model.appendAnnotation(ann)
print(sbml.writeSBMLToString(doc))
