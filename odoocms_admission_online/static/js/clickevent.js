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
	$("#uploadForm").on('submit',(function(e) {
		e.preventDefault();
		var formData = new FormData(this)
		$.ajax({
        	url: "/admissiononline/profileimage/save",
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


$(document).ready(function (e) {
	$("#document_upload_form").on('submit',(function(e) {
		e.preventDefault();
		var formData = new FormData(this)
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			data: formData,
			beforeSend: function(){$("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data)
		    {
			setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function()
	    	{
	    	}
	   });
	}));
});


//save program register
function saveProgramRegister(){
	var program_apply_for = document.getElementById("program_apply_for").value;
	if (program_apply_for.value != "") {
		odoo.define('odoocms_admission_online.clickevent', function (require) {
			"use strict";
			var ajax = require('web.ajax');
			var core = require('web.core');
			var session = require('web.session');
			var base = require('web_editor.base');
			var _t = core._t;
			base.url_translations = '/website/translations';
			var _t = core._t;

			// $(function () {
				$.ajax({
					url: "/admissiononline/programregister/save",
					method: "POST",
					dataType: "json",
					data: {program_apply_for: program_apply_for},
					success: function (data) {
						window.location.href = "/admission/registration";
					},
					error: function (error) {
						alert('error: ' + error);
					}
				});
			// });
		});
	}
}

//verify ETA Data
function verifyETEAData(){
	var test_date = document.getElementById("test_date").value;
		var applicantID = document.getElementById("applicantID").value;
		var test_score = document.getElementById("test_score").value;
		var applicant_name = document.getElementById("applicant_name").value;
		if (test_date != "" && applicantID != "" && test_score != "" && applicant_name != "") {
			odoo.define('odoocms_admission_online.clickevent', function (require) {
				"use strict";
				var ajax = require('web.ajax');
				var core = require('web.core');
				var session = require('web.session');
				var base = require('web_editor.base');
				var _t = core._t;
				base.url_translations = '/website/translations';
				var _t = core._t;

				// $(function () {
					$.ajax({
						url: "/entrytest/verfication",
						method: "POST",
						dataType: "json",
						data: {
							test_date: test_date, applicantID: applicantID, test_score: test_score
							, applicant_name: applicant_name
						},
						success: function (data) {
							if (data.status_is == "verified") {
								alert('verified!');
								document.getElementById("verify_entrytest").value = "Verified";
							} else {
								alert("Wrong details provided! please verify it again!");
							}
						},
						error: function (error) {
							alert('error: ' + error);
						}
					});
				// });
			});
		} else {
			alert('Please fill the details first!');
		}
}


//Final confirmation on checkBoxes
function finalConfirmation(){
	var final_confirmation = document.getElementById('final_confirmation');
	var final_agreement = document.getElementById('final_agreement');
	var final_terms_agreement = document.getElementById('final_terms_agreement');

	if (final_agreement.checked == true && final_terms_agreement.checked == true) {
		odoo.define('odoocms_admission_online.clickevent', function (require) {
			"use strict";
			var ajax = require('web.ajax');
			var core = require('web.core');
			var session = require('web.session');
			var base = require('web_editor.base');
			var _t = core._t;
			base.url_translations = '/website/translations';
			var _t = core._t;

			// $(function () {
				$.ajax({
					url: "/application/change/state",
					method: "POST",
					dataType: "json",
					data: {},
					success: function (data) {
						if (data.state == "submit") {
							alert('submit!');
							window.location.href = "/admission/registration";
							//document.getElementById("verify_eta").value= "Verified";
						} else {
							alert("Somthing went wrong!");
						}
					},
					error: function (error) {
						alert('error: ' + error);
					}
				});
			// });
		});
	} else {
		alert("Please accept the conditions first!");
	}
}

function changeDegreeLeve() {
	var row_inter_subject = document.getElementById("row_inter_subject");
	var inter_degree = document.getElementById("inter_degree");
	if (inter_degree.value == 'A-Level'){
		row_inter_subject.style.display = "none";
	}
	else {
		row_inter_subject.style.display = "block";
	}
}
function InterEduc() {
	var MatricModal = document.getElementById("MatricModal");
	var IntermediateModal = document.getElementById("IntermediateModal");
	MatricModal.style.display = "none";
	IntermediateModal.style.display = "block";
}
//InterEducationSave
function SaveInterEducation(){

	var intertotalmarks = document.getElementById('intertotalmarks');
	var interbtainedmarks = document.getElementById('interbtainedmarks');
	var inter_degree = document.getElementById('inter_degree');
	var inter_pass_year = document.getElementById('inter_pass_year');
	var inter_board = document.getElementById('inter_board');
	var inter_subject = document.getElementById('inter_subject');
	var repeat_times = document.getElementById('repeat_times');
	// var is_additional = document.getElementById('is_additional');
	var application_id = document.getElementById("application_id");
	var IntermediateModal = document.getElementById("IntermediateModal");

	odoo.define('odoocms_admission_online.clickevent', function (require) {
			"use strict";
			var ajax = require('web.ajax');
			var core = require('web.core');
			var session = require('web.session');
			var base = require('web_editor.base');
			var _t = core._t;
			base.url_translations = '/website/translations';
			var _t = core._t;

			var is_additional = "";
			if ($('#is_additional').is(":checked"))
				{
				 is_additional = "True";
				}

			// $(function() {
					$.ajax({
						url: "/admission/education/inter/save",
						method: "POST",
						dataType: "json",
						data: {
							application_id:application_id.value, inter_board:inter_board.value, inter_degree:inter_degree.value,inter_pass_year:inter_pass_year.value,
							inter_subject:inter_subject.value, intertotalmarks:intertotalmarks.value,
							interbtainedmarks:interbtainedmarks.value, repeat_times:repeat_times.value, is_additional:is_additional
							},
						success: function( data ) {
						},
						error: function (error) {
						   alert('error: ' + error);
						}
						});
			// });
			});
	IntermediateModal.style.display = "none";
}
function InterCloseDialog() {
	var IntermediateModal = document.getElementById("IntermediateModal");
	IntermediateModal.style.display = "none";
}

function MatricEdu() {
	var MatricModal = document.getElementById("MatricModal");
	var IntermediateModal = document.getElementById("IntermediateModal");
	MatricModal.style.display = "block";
	IntermediateModal.style.display = "none";
}
//MatricEducationSave
function saveMatricEducation(){
	var matrictotalmarks = document.getElementById('matrictotalmarks');
	var matricobtainedmarks = document.getElementById('matricobtainedmarks');
	var matric_degree = document.getElementById('matric_degree');
	var matric_pass_year = document.getElementById('matric_pass_year');
	var matric_board = document.getElementById('matric_board');
	var matric_subject = document.getElementById('matric_subject');

	var application_id = document.getElementById("application_id");
	var MatricModal = document.getElementById("MatricModal");

		odoo.define('odoocms_admission_online.clickevent', function (require) {
				"use strict";
				var ajax = require('web.ajax');
				var core = require('web.core');
				var session = require('web.session');
				var base = require('web_editor.base');
				var _t = core._t;
				base.url_translations = '/website/translations';
				var _t = core._t;

				// $(function() {
						$.ajax({
							url: "/admission/education/matric/save",
							method: "POST",
							dataType: "json",
							data: {application_id:application_id.value, matric_board:matric_board.value, matric_degree:matric_degree.value,matric_pass_year:matric_pass_year.value,
								matric_subject:matric_subject.value, matrictotalmarks:matrictotalmarks.value, matricobtainedmarks:matricobtainedmarks.value},
							success: function( data ) {
								//alert(data.status_is);
							},
							error: function (error) {
							   alert('error: ' + error);
							}
							});
				// });
				});
		MatricModal.style.display = "none";
}
function MatricCloseDialog() {
	var MatricModal = document.getElementById("MatricModal");
	MatricModal.style.display = "none";
}

function isSameAddress(){
	var street = document.getElementById("street");
	var street2 = document.getElementById("street2");
	var city = document.getElementById("city");
	var country = document.getElementById("country");

	var checkBox_is_same_address = document.getElementById("is_same_address");

	if(checkBox_is_same_address.checked){
			street.value = document.getElementById("per_street").value;
			street2.value = document.getElementById("per_street2").value;
			city.value = document.getElementById("per_city").value;
			country.value = document.getElementById("per_country").value;

			street.disabled = true;
			street2.disabled = true;
			city.disabled = true;
			country.disabled = true;
		}
		else{
			street.value = "";
			street2.value = "";
			city.value = "";
			country.value = "";

			street.disabled = false;
			street2.disabled = false;
			city.disabled = false;
			country.disabled = false;
		}
}

function closeFinalModal(){
	var final_modal = document.getElementById('final_data_id');
	final_modal.style.display = "none";

}


	function choice1() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice1.value < 0 || choice1.value > 18 ) {
			choice1.value="0"
		}
		else{
			if(choice1.value == choice2.value || choice1.value == choice3.value || choice1.value == choice4.value || choice1.value == choice5.value ||
			choice1.value == choice6.value || choice1.value == choice7.value || choice1.value == choice8.value || choice1.value == choice9.value ||
			choice1.value == choice10.value || choice1.value == choice11.value || choice1.value == choice12.value || choice1.value == choice13.value ||
			choice1.value == choice14.value || choice1.value == choice15.value || choice1.value == choice16.value || choice1.value == choice17.value ||
			choice1.value == choice18.value){
				alert("Priority can't be same!");
				choice1.value == "0";
			}
		}
	}

	function choice2() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice2.value < 0 || choice2.value > 18 ) {
			choice2.value="0"

		}
		else{
			if(choice2.value == choice1.value || choice2.value == choice3.value || choice2.value == choice4.value || choice2.value == choice5.value ||
			choice2.value == choice6.value || choice2.value == choice7.value || choice2.value == choice8.value || choice2.value == choice9.value ||
			choice2.value == choice10.value || choice2.value == choice11.value || choice2.value == choice12.value || choice2.value == choice13.value ||
			choice2.value == choice14.value || choice2.value == choice15.value || choice2.value == choice16.value || choice2.value == choice17.value ||
			choice2.value == choice18.value){
				alert("Priority can't be same!");
				choice2.value == "0";
			}
		}
	}
	function choice3() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice3.value < 0 || choice3.value > 18 ) {
			choice3.value="0"
		}
		else{
			if(choice3.value == choice1.value || choice3.value == choice2.value || choice3.value == choice4.value || choice3.value == choice5.value ||
			choice3.value == choice6.value || choice3.value == choice7.value || choice3.value == choice8.value || choice3.value == choice9.value ||
			choice3.value == choice10.value || choice3.value == choice11.value || choice3.value == choice12.value || choice3.value == choice13.value ||
			choice3.value == choice14.value || choice3.value == choice15.value || choice3.value == choice16.value || choice3.value == choice17.value ||
			choice3.value == choice18.value){
				alert("Priority can't be same!");
				choice3.value == "0";
			}
		}
	}
	function choice4() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice4.value < 0 || choice4.value > 18 ) {
			choice4.value="0"
		}
		else{
			if(choice4.value == choice1.value || choice4.value == choice2.value || choice4.value == choice3.value || choice4.value == choice5.value ||
			choice4.value == choice6.value || choice4.value == choice7.value || choice4.value == choice8.value || choice4.value == choice9.value ||
			choice4.value == choice10.value || choice4.value == choice11.value || choice4.value == choice12.value || choice4.value == choice13.value ||
			choice4.value == choice14.value || choice4.value == choice15.value || choice4.value == choice16.value || choice4.value == choice17.value ||
			choice4.value == choice18.value){
				alert("Priority can't be same!");
				choice4.value == "0";
			}
		}
	}
	function choice5() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice5.value < 0 || choice5.value > 18 ) {
			choice5.value="0"
		}
		else{
			if(choice5.value == choice1.value || choice5.value == choice2.value || choice5.value == choice3.value || choice5.value == choice4.value ||
			choice5.value == choice6.value || choice5.value == choice7.value || choice5.value == choice8.value || choice5.value == choice9.value ||
			choice5.value == choice10.value || choice5.value == choice11.value || choice5.value == choice12.value || choice5.value == choice13.value ||
			choice5.value == choice14.value || choice5.value == choice15.value || choice5.value == choice16.value || choice5.value == choice17.value ||
			choice5.value == choice18.value){
				alert("Priority can't be same!");
				choice5.value == 0;
			}
		}
	}
	function choice6() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice6.value < 0 || choice6.value > 18 ) {
			choice6.value="0"
		}
		else{
			if(choice6.value == choice1.value || choice6.value == choice2.value || choice6.value == choice3.value || choice6.value == choice4.value ||
			choice6.value == choice5.value || choice6.value == choice7.value || choice6.value == choice8.value || choice6.value == choice9.value ||
			choice6.value == choice10.value || choice6.value == choice11.value || choice6.value == choice12.value || choice6.value == choice13.value ||
			choice6.value == choice14.value || choice6.value == choice15.value || choice6.value == choice16.value || choice6.value == choice17.value ||
			choice6.value == choice18.value){
				alert("Priority can't be same!");
				choice6.value == 0;
			}
		}
	}
	function choice7() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice7.value < 0 || choice7.value > 18 ) {
		choice7.value="0"
		}
		else{
			if(choice7.value == choice1.value || choice7.value == choice2.value || choice7.value == choice3.value || choice7.value == choice4.value ||
			choice7.value == choice5.value || choice7.value == choice6.value || choice7.value == choice8.value || choice7.value == choice9.value ||
			choice7.value == choice10.value || choice7.value == choice11.value || choice7.value == choice12.value || choice7.value == choice13.value ||
			choice7.value == choice14.value || choice7.value == choice15.value || choice7.value == choice16.value || choice7.value == choice17.value ||
			choice7.value == choice18.value){
				alert("Priority can't be same!");
				choice7.value == 0;
			}
		}
	}
	function choice8() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice8.value < 0 || choice8.value > 18 ) {
			choice8.value="0"
		}
		else{
			if(choice8.value == choice1.value || choice8.value == choice2.value || choice8.value == choice3.value || choice8.value == choice4.value ||
			choice8.value == choice5.value || choice8.value == choice6.value || choice8.value == choice7.value || choice8.value == choice9.value ||
			choice8.value == choice10.value || choice8.value == choice11.value || choice8.value == choice12.value || choice8.value == choice13.value ||
			choice8.value == choice14.value || choice8.value == choice15.value || choice8.value == choice16.value || choice8.value == choice17.value ||
			choice8.value == choice18.value){
				alert("Priority can't be same!");
				choice8.value == 0;
			}
		}
	}
	function choice9() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice9.value < 0 || choice9.value > 18 ) {
			choice9.value="0"
		}
		else{
			if(choice9.value == choice1.value || choice9.value == choice2.value || choice9.value == choice3.value || choice9.value == choice4.value ||
			choice9.value == choice5.value || choice9.value == choice6.value || choice9.value == choice7.value || choice9.value == choice8.value ||
			choice9.value == choice10.value || choice9.value == choice11.value || choice9.value == choice12.value || choice9.value == choice13.value ||
			choice9.value == choice14.value || choice9.value == choice15.value || choice9.value == choice16.value || choice9.value == choice17.value ||
			choice9.value == choice18.value){
				alert("Priority can't be same!");
				choice9.value == 0;
			}
		}
	}
	function choice10() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice10.value < 0 || choice10.value > 18 ) {
			choice10.value="0"
		}
		else{
			if(choice10.value == choice1.value || choice10.value == choice2.value || choice10.value == choice3.value || choice10.value == choice4.value ||
			choice10.value == choice5.value || choice10.value == choice6.value || choice10.value == choice7.value || choice10.value == choice8.value ||
			choice10.value == choice9.value || choice10.value == choice11.value || choice10.value == choice12.value || choice10.value == choice13.value ||
			choice10.value == choice14.value || choice10.value == choice15.value || choice10.value == choice16.value || choice10.value == choice17.value ||
			choice10.value == choice18.value){
				alert("Priority can't be same!");
				choice10.value == 0;
			}
		}
	}
	function choice11() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice11.value < 0 || choice11.value > 18 ) {
			choice11.value="0"
		}
		else{
			if(choice11.value == choice1.value || choice11.value == choice2.value || choice11.value == choice3.value || choice11.value == choice4.value ||
			choice11.value == choice5.value || choice11.value == choice6.value || choice11.value == choice7.value || choice11.value == choice8.value ||
			choice11.value == choice9.value || choice11.value == choice10.value || choice11.value == choice12.value || choice11.value == choice13.value ||
			choice11.value == choice14.value || choice11.value == choice15.value || choice11.value == choice16.value || choice11.value == choice17.value ||
			choice11.value == choice18.value){
				alert("Priority can't be same!");
				choice11.value == 0;
			}
		}
	}
	function choice12() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice12.value < 0 || choice12.value > 18 ) {
			choice12.value="0"
		}
		else{
			if(choice12.value == choice1.value || choice12.value == choice2.value || choice12.value == choice3.value || choice12.value == choice4.value ||
			choice12.value == choice5.value || choice12.value == choice6.value || choice12.value == choice7.value || choice12.value == choice8.value ||
			choice12.value == choice9.value || choice12.value == choice10.value || choice12.value == choice11.value || choice12.value == choice13.value ||
			choice12.value == choice14.value || choice12.value == choice15.value || choice12.value == choice16.value || choice12.value == choice17.value ||
			choice12.value == choice18.value){
				alert("Priority can't be same!");
				choice12.value == 0;
			}
		}
	}
	function choice13() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice13.value < 0 || choice13.value > 18 ) {
			choice13.value="0"
		}
		else{
			if(choice13.value == choice1.value || choice13.value == choice2.value || choice13.value == choice3.value || choice13.value == choice4.value ||
			choice13.value == choice5.value || choice13.value == choice6.value || choice13.value == choice7.value || choice13.value == choice8.value ||
			choice13.value == choice9.value || choice13.value == choice10.value || choice13.value == choice11.value || choice13.value == choice12.value ||
			choice13.value == choice14.value || choice13.value == choice15.value || choice13.value == choice16.value || choice13.value == choice17.value ||
			choice13.value == choice18.value){
				alert("Priority can't be same!");
				choice13.value == 0;
			}
		}
	}
	function choice14() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice14.value < 0 || choice14.value > 18 ) {
			choice14.value="0"
		}
		else{
			if(choice14.value == choice1.value || choice14.value == choice2.value || choice14.value == choice3.value || choice14.value == choice4.value ||
			choice14.value == choice5.value || choice14.value == choice6.value || choice14.value == choice7.value || choice14.value == choice8.value ||
			choice14.value == choice9.value || choice14.value == choice10.value || choice14.value == choice11.value || choice14.value == choice12.value ||
			choice14.value == choice13.value || choice14.value == choice15.value || choice14.value == choice16.value || choice14.value == choice17.value ||
			choice14.value == choice18.value){
				alert("Priority can't be same!");
				choice14.value == 0;
			}
		}
	}
	function choice15() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice15.value < 0 || choice15.value > 18 ) {
			choice15.value="0"
		}
		else{
			if(choice15.value == choice1.value || choice15.value == choice2.value || choice15.value == choice3.value || choice15.value == choice4.value ||
			choice15.value == choice5.value || choice15.value == choice6.value || choice15.value == choice7.value || choice15.value == choice8.value ||
			choice15.value == choice9.value || choice15.value == choice10.value || choice15.value == choice11.value || choice15.value == choice12.value ||
			choice15.value == choice13.value || choice15.value == choice14.value || choice15.value == choice16.value || choice15.value == choice17.value ||
			choice15.value == choice18.value){
				alert("Priority can't be same!");
				choice15.value == 0;
			}
		}
	}
	function choice16() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice16.value < 0 || choice16.value > 18 ) {
			choice16.value="0"
		}
		else{
			if(choice16.value == choice1.value || choice16.value == choice2.value || choice16.value == choice3.value || choice16.value == choice4.value ||
			choice16.value == choice5.value || choice16.value == choice6.value || choice16.value == choice7.value || choice16.value == choice8.value ||
			choice16.value == choice9.value || choice16.value == choice10.value || choice16.value == choice11.value || choice16.value == choice12.value ||
			choice16.value == choice13.value || choice16.value == choice14.value || choice16.value == choice15.value || choice16.value == choice17.value ||
			choice16.value == choice18.value){
				alert("Priority can't be same!");
				choice16.value == 0;
			}
		}
	}
	function choice17() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice17.value < 0 || choice17.value > 18 ) {
			choice17.value="0"
		}
		else{
			if(choice17.value == choice1.value || choice17.value == choice2.value || choice17.value == choice3.value || choice17.value == choice4.value ||
			choice17.value == choice5.value || choice17.value == choice6.value || choice17.value == choice7.value || choice17.value == choice8.value ||
			choice17.value == choice9.value || choice17.value == choice10.value || choice17.value == choice11.value || choice17.value == choice12.value ||
			choice17.value == choice13.value || choice17.value == choice14.value || choice17.value == choice15.value || choice17.value == choice16.value ||
			choice17.value == choice18.value){
				alert("Priority can't be same!");
				choice17.value == 0;
			}
		}
	}
	function choice18() {
	// code of choice selection
	var choice1 = document.getElementById("choice1");
	var choice2 = document.getElementById("choice2");
	var choice3 = document.getElementById("choice3");
	var choice4 = document.getElementById("choice4");
	var choice5 = document.getElementById("choice5");
	var choice6 = document.getElementById("choice6");
	var choice7 = document.getElementById("choice7");
	var choice8 = document.getElementById("choice8");
	var choice9 = document.getElementById("choice9");
	var choice10 = document.getElementById("choice10");
	var choice11 = document.getElementById("choice11");
	var choice12 = document.getElementById("choice12");
	var choice13 = document.getElementById("choice13");
	var choice14 = document.getElementById("choice14");
	var choice15 = document.getElementById("choice15");
	var choice16 = document.getElementById("choice16");
	var choice17 = document.getElementById("choice17");
	var choice18 = document.getElementById("choice18");
		if(choice18.value < 0 || choice18.value > 18 ) {
			choice18.value="0"
		}
		else{
			if(choice18.value == choice1.value || choice18.value == choice2.value || choice18.value == choice3.value || choice18.value == choice4.value ||
			choice18.value == choice5.value || choice18.value == choice6.value || choice18.value == choice7.value || choice18.value == choice8.value ||
			choice18.value == choice9.value || choice18.value == choice10.value || choice18.value == choice11.value || choice18.value == choice12.value ||
			choice18.value == choice13.value || choice18.value == choice14.value || choice18.value == choice15.value || choice18.value == choice16.value ||
			choice18.value == choice17.value){
				alert("Priority can't be same!");
				choice18.value == 0;
			}
		}
	}
