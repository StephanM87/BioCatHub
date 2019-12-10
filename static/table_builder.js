"use strict"

class Table {

    constructor(parameter, substrates) {
        this.parameter = parameter;
        this.substrates = substrates;
    }
    

    CreateTable(){
        
        let Reaction_Input = parameterGrabber();
        let Parameter = Object.keys(Reaction_Input["Parameters"])
        console.log(Parameter)

        let div = document.getElementById("divelement");
        /*while (div.hasChildNodes()) {
            div.removeChild(div.firstChild);
            console.log("removed");


        }
        
        /*let child = div.childNodes[0];
        
        div.removeChild(child) */
        div.setAttribute("class", "eight columns");

        // Initialize table

        let table = document.createElement("table");
     

        for (let i = 0; i<Parameter.length; i++) {

            let Head_row = document.createElement("tr");

            let table_head = document.createElement("th");
            table_head.appendChild(document.createTextNode(Parameter[i]))
            let head_value = document.createElement("th");
            head_value.appendChild(document.createTextNode(Reaction_Input["Parameters"][Parameters[i]]))
            Head_row.appendChild(table_head);
            Head_row.appendChild(head_value);
            table.appendChild(Head_row);
        }

        let heading = document.createElement("h2");
        heading.appendChild(document.createTextNode("Data to submit"));
        div.appendChild(heading);   
        div.appendChild(table);
    

// Add Substrates and Products

        let table_substrates = document.createElement("table");
        table_substrates.setAttribute("Id", "table_substrates")
        
        let Reactand_name = Reaction_Input["Reactant_name"];
        let concentration = Reaction_Input["concentration_value"];
        let unit = Reaction_Input["unit"];
        let kind = Reaction_Input["reactant_kind"];

        console.log(Reactand_name)
        let Reaction_table = [Reactand_name, concentration, unit, kind]

       
        let table_reactants_head_row = document.createElement("tr");
        
        let table_reactants_head_inputs = ["Reactant name", "concentration value", "concentration unit", "reactant kind"]

        for (let i =0; i<4; i++){
            let table_reactants_head = document.createElement("th");
            table_reactants_head.appendChild(document.createTextNode(table_reactants_head_inputs[i]));
            table_reactants_head_row.appendChild(table_reactants_head)
        }


        table_substrates.appendChild(table_reactants_head_row)


        let table_body = document.createElement("tbody");


        for(let i = 0; i<Reactand_name.length; i++){

            let row = document.createElement("tr");

            for(let j = 0; j<=3; j++){

                let cell = document.createElement("td");
                let cellelement = Reaction_table[j];
                let cellText = document.createTextNode(cellelement[i])
                console.log(cellText);

                cell.appendChild(cellText);
                row.appendChild(cell);
            }

            table_body.appendChild(row);
        }
        table_substrates.appendChild(table_body);
        let heading_reactants = document.createElement("h2");
        heading_reactants.appendChild(document.createTextNode("Reactands"));
        div.appendChild(heading_reactants);
        div.appendChild(table_substrates);
        let Button = document.createElement("Button");
        Button.setAttribute("id", "remove_button");
        Button.appendChild(document.createTextNode("Correct Parameters"))
        div.appendChild(Button);

        let Button_correct_parameters = document.createElement("Button");
        Button_correct_parameters.setAttribute("Id", "submit_parameters");
        Button_correct_parameters.appendChild(document.createTextNode("Send parameters"))
        div.appendChild(Button_correct_parameters);
        

        }   


    

}

function deleteTable(){

    let div = document.getElementById("divelement");
    while (div.hasChildNodes()) {
        div.removeChild(div.firstChild);
        console.log("removed");
        }
    document.querySelector("#General_information").scrollIntoView({
        behavior: 'smooth'
    });
    

}

