
function parameterGrabber (){

        let Reactant_name = [];
        let concentration_value = [];
        let unit = [];
        let reactant_kind = [];
        let test_reactants = [];
        let test_concentration_values = [];
        let Reaction_parameters = [];
        let Reactants = {};
        let Params = {};


    //$("form").on("submit", function(event) {
        //event.preventDefault();

        let Parameters = parameterList();
        //console.log(Parameters.length)
        
        for (let i=0; i < Parameters.length; i++){
            $("."+Parameters[i]).each(function(){
                Reaction_parameters.push($(this).val())
            })
        } 

        for (let i =0; i<Parameters.length; i++){
            declaration = Parameters[i];
            Params[declaration] = Reaction_parameters[i];
            Reactants["Parameters"]=Params
        }




        $(".Substrate_name").each(function(){
            test_reactants.push($(this).val());
        })
        $(".concentration_value").each(function(){
            test_concentration_values.push($(this).val());
        })       

        if(test_reactants.includes("") || test_concentration_values.includes("") == true){              
            Reactant_name = [];
            concentration_value = [];
            unit = [];
            reactant_kind = [];
            test_reactants = [];
            test_concentration_values = [];

            alert("Values are missing");
        }
        else {
            $('.Substrate_name').each(function(){
                //let Reactant = $(this);
                Reactant_name.push($(this).val());
            })
            $('.concentration_value').each(function(){
                //let concentration = $(this);
                concentration_value.push($(this).val());
            })
            $('.concentration_unit').each(function(){
                //let unit_value = $(this);
                unit.push($(this).val());
            })
            $('.reactant_kind').each(function(){
                //let reactant = $(this);
                reactant_kind.push($(this).val());
            })



            
            Reactants["Reactant_name"]= Reactant_name;
            Reactants["concentration_value"]= concentration_value;
            Reactants["unit"]= unit;
            Reactants["reactant_kind"]= reactant_kind;
           
            //console.log(Reactants["Parameters"])
            //console.log(Reactants)

            //console.log(Object.keys(Reactants))

            //console.log(Reactant_name);
            //console.log(concentration_value);
            //console.log(unit);
            //console.log(reactant_kind);
            return Reactants;
        };
  
};