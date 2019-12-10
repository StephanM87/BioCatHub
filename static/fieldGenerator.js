function field_generator(){

    let div = document.getElementById('Reactants');

    let Row = document.createElement("div");
    Row.setAttribute("class", 'twelve columns');
    let p = document.createElement("p");
    /* Create Substrate Name */
    let div_SubstrateName = document.createElement("div");
    div_SubstrateName.setAttribute("class", "three columns");
    let SubstrateName = document.createElement("input");
    SubstrateName.setAttribute("name", "Substance_37");
    SubstrateName.setAttribute("type", "text");
    SubstrateName.setAttribute("class", "Substrate_name");
    SubstrateName.setAttribute("kind", "Reactant");
    div_SubstrateName.appendChild(SubstrateName);
    p.appendChild(div_SubstrateName);
    /* Create Concentration_value */
    let div_concentration_value = document.createElement("div");
    div_concentration_value.setAttribute("class", "three columns");
    let concentration_value = document.createElement("input");
    concentration_value.setAttribute("name", "concentration_value");
    concentration_value.setAttribute("type", "text");
    concentration_value.setAttribute("class", "concentration_value");
    div_concentration_value.appendChild(concentration_value);
    p.appendChild(div_concentration_value);
    /* Create concentration_unit */
    let concentration_units = ["mol/L", "mmol/L", "µmol/L", "nmol/L", "mL/L", "µg/L"];
    let count_concentration_units = concentration_units.length;
    console.log(count_concentration_units);
    let div_concentration_unit = document.createElement("div");
    div_concentration_unit.setAttribute("class", "two columns");
    let concentration_unit = document.createElement("select");
    concentration_unit.setAttribute("name", "concentration_unit");
    concentration_unit.setAttribute("class", "concentration_unit");
    let i 
    for (i = 0; i <= count_concentration_units-1; i=i+1) {

            let option = document.createElement("option");
            option.setAttribute("value", concentration_units[i]);
            let text = document.createTextNode(concentration_units[i]);
            option.appendChild(text);
            concentration_unit.appendChild(option);

        };

    div_concentration_unit.appendChild(concentration_unit);
    p.appendChild(div_concentration_unit);

    /* Create Reactant kind*/
    let reactant_kinds = ["substrate", "product", "cofactor", "additive"];
    let count_reactant_kinds = reactant_kinds.length;
    console.log(count_reactant_kinds);

    let div_reactant_kind = document.createElement("div");
    div_reactant_kind.setAttribute("class", "two columns");
    let reactant_kind = document.createElement("select");
    reactant_kind.setAttribute("name", "reactant_kind");
    reactant_kind.setAttribute("class", "reactant_kind");
    let a 

    for (a = 0; a <= count_reactant_kinds-1; a=a+1) {

            let option_rk = document.createElement("option");
            option_rk.setAttribute("value", reactant_kinds[a]);
            let text_rk = document.createTextNode(reactant_kinds[a]);
            option_rk.appendChild(text_rk);
            reactant_kind.appendChild(option_rk);

        };

    div_reactant_kind.appendChild(reactant_kind);
    p.appendChild(div_reactant_kind);

    /* Create delete button*/

    let div_delete = document.createElement("div");
    div_delete.setAttribute("class", "one column");
    div_delete.setAttribute("class", "delete_button");

    let div_head = document.createElement("h3");
    /*div_head.setAttribute("class", "delete_button");*/
    let delete_button = document.createTextNode("-");

    div_head.appendChild(delete_button);
    div_delete.appendChild(div_head);
    p.appendChild(div_delete)
    div.appendChild(p);

}