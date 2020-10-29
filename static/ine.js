var boton = document.getElementById('identificacion');
var progreso = 0;
boton.addEventListener("click",function (){

alert("Documento validados correctamente")
    
});

jQuery('#identificacion').click(function(){
    let valor = $('#iden').val();
    console.log("se ejecuto jquery");
    uploadFile(valor);
});

function uploadFile(valor){
    console.log("llego")
    var form_data = new FormData();
    var ins = document.getElementById('iden').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('iden').files[x]);
    }

    $.ajax({
        url: '/Ine',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          console.log("success documento");
          console.log(data);
          progreso= progreso + 25;
          console.log("progreso " + progreso);
          $("#progress").css("width",progreso+"%");
          $("#progress").text(progreso+"%");
        },

    });
}


var boton2 = document.getElementById('comprobante');
boton2.addEventListener("click",function (){

alert("Documento validados correctamente")
    
});

jQuery('#comprobante').click(function(){
    let valor = $('#comp').val();
    console.log("se ejecuto jquery");
    uploadFile2(valor);
});

function uploadFile2(valor){
    console.log("llego")
    var form_data = new FormData();
    var ins = document.getElementById('comp').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('comp').files[x]);
    }

    $.ajax({
        url: '/COMPROBANTE',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          console.log("success docuemtno arriba");
          console.log(data);
          
          progreso= progreso + 25;
          console.log("progreso " + progreso);
          $("#progress").css("width",progreso+"%");
          $("#progress").text(progreso+"%");
        },

    });
}

var boton3 = document.getElementById('escolaridad');
boton3.addEventListener("click",function (){

alert("Documento validados correctamente")
    
});

jQuery('#escolaridad').click(function(){
    let valor = $('#esc').val();
    console.log("se ejecuto jquery");
    uploadFile3(valor);
});

function uploadFile3(valor){
    console.log("llego")
    var form_data = new FormData();
    var ins = document.getElementById('esc').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('esc').files[x]);
    }

    $.ajax({
        url: '/ESCOLARIDAD',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          console.log("success docuemtno arriba");
          console.log(data);
          console.log("progreso " + progreso);
          $("#progress").css("width",progreso+"%");
          $("#progress").text(progreso+"%");
        },

    });
}