"use strict"
window.addEventListener("load", function(){
    localStorage.clear();
    

    //$(document).ready(function() {
        $('#Reactants1').click(function(){
            field_generator();
        });

        $('.delete_button').click(function(){
            this.parentNode.parentNode.removeChild(this.parentNode);
        })
            
        $("#submit1").click(function(event) {
            //event.preventDefault();
            let form = new FormData();
            let file = document.getElementById("input");
            let data = JSON.stringify(parameterGrabber());

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
        
    //});
        

},false)

