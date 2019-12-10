"use strict"
window.addEventListener("load", function(){
    localStorage.clear();
    

    //$(document).ready(function() {
        $('#Reactants1').click(function(){
            field_generator();
        

            $('.delete_button').click(function(){
                console.log("deleted");
                
            
                
                this.parentNode.parentNode.removeChild(this.parentNode);
            }); 
        });
            
        $("#submit1").click(function(event) {
            
            //event.preventDefault();
            //let form = new FormData();
            //let file = document.getElementById("input");

            let Reaction_data = new Table("Hallo", "Hallo");
            Reaction_data.CreateTable();
            document.querySelector('#table_substrates').scrollIntoView({
                behavior: 'smooth'
              });

              $('#remove_button').click(function(){
                console.log("Hallo");
                deleteTable();
            })

            
            
            //let element = document.getElementById("table_substrates");
            //element.scrollIntoView(behavior= 'smooth');

        $('#submit_parameters').click(function(){
            let form = new FormData();
            let file = document.getElementById("input");
            let data = JSON.stringify(parameterGrabber());
            console.log(data);
            form.append("data", data);
            form.append("filename", file.files[0]);
            console.log(form);
           $.ajax({
                url: "/transmission",
                type: 'POST',
                processData: false,
                contentType: false,
                dataType: "json",
                data: form,
                success: function(resp){
                    //console.log(resp);
                                       
                    console.log("Juhuuuu")
                    window.location.href= "/transmission/Auswertung";
                },
                error: function(){
                    console.log("Neieeeeein")
                }
            });
        });
    });
            
            

    

        

            /*form.append("data", data);
            form.append("filename", file.files[0]);
            console.log(form);
           $.ajax({
                url: "/transmission",
                type: 'POST',
                processData: false,
                contentType: false,
                dataType: "json",
                data: form,
                success: function(resp){
                    //console.log(resp);
                                       
                    console.log("Juhuuuu")
                    window.location.href= "/transmission/Auswertung";
                },
                error: function(){
                    console.log("Neieeeeein")
                }
            });
        });*/
        
    //});
        

},false)

