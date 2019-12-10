
"use strict"

window.addEventListener("load", function(){
localStorage.clear();
let img = document.getElementById("picture")
let img_source = "/static/Hallo.svg";
let attribute = document.createAttribute("src");
attribute.value = img_source

img.setAttribute("src", img_source);


console.log("Juhuuuu");
console.log(data);
console.log(data.Reactant_name);

let Reactand_name = data.Reactant_name;
let concentration = data.concentration_value;
let unit = data.unit;
let kind = data.reactant_kind;


console.log(Reactand_name)
console.log(concentration)
console.log(unit)
console.log(kind)

let Reaction_table = [Reactand_name, concentration, unit, kind]



console.log("Hallo Jan")
let reactand_table = document.getElementById("reactand_table");
let d = document;

let table_body = document.createElement("tbody");


for(let i = 0; i<Reactand_name.length; i++){

    let row = document.createElement("tr");

    for(let j = 0; j<=3; j++){

        let cell = document.createElement("td");
        let cellelement = Reaction_table[j];
        let cellText = document.createTextNode(cellelement[i])

        cell.appendChild(cellText);
        row.appendChild(cell);
    }

    table_body.appendChild(row);
}

reactand_table.appendChild(table_body);
})