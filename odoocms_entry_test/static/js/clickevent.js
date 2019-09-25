
// for image prview 
// this is out of window.onload because it is applied on html with onchange attribute of form
function showPreview(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
			$("#targetLayer").html('<img src="'+e.target.result+'" width="200px" height="200px" class="upload-preview" />');
			$("#targetLayer").css('opacity','0.8');
			$("#targetLayer2").html('<img src="'+e.target.result+'" width="200px" height="200px" class="upload-preview" />');
			$("#targetLayer2").css("display", "none");
			$(".icon-choose-image").css('opacity','0');
        }
		fileReader.readAsDataURL(objFileInput.files[0]);
    }
	

}
// Image preview code end
$(document).ready(function (e) {
	$("#image-upload-form").on('submit',(function(e) {
		e.preventDefault();
		var formData = new FormData(this)
		$.ajax({
        	url: "/entry/profileimage/save",
			type: "POST",
			data: formData,
			beforeSend: function(){$("#body-overlay").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data)
		    {
				$("#targetLayer2").css("display", "block");
				$("#targetLayer").css("display", "none");
				$("#uploaded_image").css("display", "none");
				$(".icon-choose-image").css('opacity','0.5');
			// $("#targetLayer").html('<img src="'+e.target.result+'" width="200px" height="200px" class="upload-preview" />');
			// $("#targetLayer").css('opacity','1');
			setInterval(function() {$("#body-overlay").hide(); },100);
			},
		  	error: function() 
	    	{
	    	} 	        
	   });
	}));
});

function finalConfirmation(){
	var final_agreement = document.getElementById('final_agreement');
	var final_terms_agreement = document.getElementById('final_terms_agreement');
	if(final_agreement.checked == true && final_terms_agreement.checked == true ){
			odoo.define('odoocms_entry_test.clickevent', function (require) {
			"use strict";
			var ajax = require('web.ajax');
			var core = require('web.core');
			var session = require('web.session');
			var base = require('web_editor.base');
			var _t = core._t;
			base.url_translations = '/website/translations';
			var _t = core._t;

			var mobile = $('#mobile').val();

			$(function() {
					$.ajax({
						url: "/entry/application/change/state",
						method: "POST",
						dataType: "json",
						data: {mobile:mobile},
						success: function( data ) {
							if(data.state == "submit"){
								window.location.href= "/entrytest/registration";
							}
							else{
								alert("Somthing went wrong!");
							}
						},
						error: function (error) {
						   alert('error: ' + error);
						}
						});
			});
			});
	}
	else{
		alert("Please accept the conditions first!");
	}
}

function finalModalClose(){
	var final_modal = document.getElementById('final_data_id');
	final_modal.style.display = "none";
}

function IsSameAdress(){
	var street = document.getElementById("street");
	var street2 = document.getElementById("street2");
	var checkBox_is_same_address = document.getElementById("is_same_address");
	if(checkBox_is_same_address.checked){
		street.value = document.getElementById("per_street").value;
		street2.value = document.getElementById("per_street2").value;

		street.disabled = true;
		street2.disabled = true;
	}
	else{
		street.value = "";
		street2.value = "";

		street.disabled = false;
		street2.disabled = false;
	}
}
