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


app = Flask(__name__)
app.config["DEBUG"] = True
app.env=True

@app.route("/")
def start():
    return render_template("Test.html")

input_values = dict()


@app.route("/transmission", methods = ['GET','POST'])
def transmission():    
    
    if os.path.isfile("static\Hallo.svg") == True:
        os.remove("static\Hallo.svg")
    else:
        None
    
    if os.path.isdir("C:/enzymeML") == True:
        None
    else:
        os.mkdir("C:/enzymeML")

    if request.method == "POST":
        input_values.clear()
        
        data = request.form.to_dict()
        json_params = json.loads(data["data"].replace("'", "\""))
        params_enzymeML = json_params["Parameters"]
        params_enzymeML["Reactant_name"] = json_params["Reactant_name"]
        params_enzymeML["concentration_value"] = json_params["concentration_value"]
        params_enzymeML["unit"] = json_params["unit"]
        params_enzymeML["reactant_kind"] = json_params["reactant_kind"]
        
        
        
        
        
        df = pd.read_excel(request.files["filename"])
        print(data)
        
        #print(df)

        experiment = EnzymeMLwriter(params_enzymeML, "EnzymeML.xml", request.files["filename"])
        experiment.write()
    
        fig, ax = plt.subplots()
        
        sns.set_style("white")
    
   
        #print(type(df))
        headers = df.columns.values
        #print(headers)
        #print(df)
        concentrations = df[headers[0]]
        #print(concentrations)
        graphs = np.delete(headers, 0)
        #print(graphs)

        


        for i in graphs:
            ax.plot(concentrations, df[i], color = "black", marker = "^")
          
        plt.savefig("static/Hallo.svg", type="svg")
     
        
 

        input_values["data"] = json_params

        return jsonify({"success": 'Oh Yeah'})
     
    return render_template("TEEDtransmissionindex.html")

@app.route("/transmission/Auswertung", methods = ['GET','POST'])
def Auswertung():
        
  
    values = input_values["data"]
    print(values)
   



   

     
    return render_template("Auswertung.html", values = values)
        

        



if __name__=="__main__":
    app.run(port=8000, debug=True)


