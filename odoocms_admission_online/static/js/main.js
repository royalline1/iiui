$(function(){
	$("#smart-form-admission").steps({
		bodyTag: "fieldset",
		headerTag: "h2",
		transitionEffect: "slideLeft",
		titleTemplate: "<span class='number'>#index#</span> #title#",
		labels: {
			finish: "Submit Form",
			next: "Save & Next",
			previous: "Go Back",
			loading: "Loading...",
			templete:"admission_application",
		},
		// onStepChanging: function (event, currentIndex, newIndex){
			// if (currentIndex > newIndex){return true; }
			// var form = $(this);
			// if (currentIndex < newIndex){}
			// return form.valid();
		// },
		// onStepChanged: function (event, currentIndex, priorIndex){
		// },
		// onFinishing: function (event, currentIndex){
			// var form = $(this);
			// form.validate().settings.ignore = ":disabled";
			// return form.valid();
		// },
		// onFinished: function (event, currentIndex){
			// var form = $(this);
		// }
	})//.validate({
		// errorClass: "state-error",
		// validClass: "state-success",
		// errorElement: "em",
		// onkeyup: false,
		// onclick: false,
		// rules: {
			// name: {
				// required: true
			// },
			// father_name: {
				// required: true
			// },
			// guardian_name: {
				// required: true,
				// number: true
			// },
			// guardian_cnic: {
				// required: true
			// },					
			// dob: {
				// required: true
			// },
			// cnic:{
				// required: true
			// },
			// mobile:{
				// required: true
			// }					
		// },
		// messages: {
			// name: {
				// required: "Please enter Your Name"
			// },
			// father_name: {
				// required: "Please enter father name"
			// },
			// guardian_name: {
				// required: 'Please enter guardian name'
			// },
			// guardian_cnic: {
				// required: 'Please enter guardian cnic',
				// // number: 'Please enter numbers only'
			// },					
			// dob: {
				// required: "Please add Date Of Birth"
			// },
			// cnic:{
				// required: 'Please enter cnic'
			// },
			// mobile:{
				// required: 'Please enter mobile number'
			// }					
		// },
		// highlight: function(element, errorClass, validClass) {
			// $(element).closest('.field').addClass(errorClass).removeClass(validClass);
		// },
		// unhighlight: function(element, errorClass, validClass) {
			// $(element).closest('.field').removeClass(errorClass).addClass(validClass);
		// },
		// errorPlacement: function(error, element) {
			// if (element.is(":radio") || element.is(":checkbox")) {
				// element.closest('.option-group').after(error);
			// } else {
				// error.insertAfter(element.parent());
			// }
		// }
	
	// });
	
	// /* Project datepicker range
	// ----------------------------------------------- */			
	// $("#start_date").datepicker({
		// defaultDate: "+1w",
		// changeMonth: false,
		// numberOfMonths: 1,
		// prevText: '<i class="fa fa-chevron-left"></i>',
		// nextText: '<i class="fa fa-chevron-right"></i>',
		// onClose: function( selectedDate ) {
			// $( "#end_date" ).datepicker( "option", "minDate", selectedDate );
		// }
	// });
	
	// $("#end_date").datepicker({
		// defaultDate: "+1w",
		// changeMonth: false,
		// numberOfMonths: 1,
		// prevText: '<i class="fa fa-chevron-left"></i>',
		// nextText: '<i class="fa fa-chevron-right"></i>',			
		// onClose: function( selectedDate ) {
			// $( "#start_date" ).datepicker( "option", "maxDate", selectedDate );
		// }
	// });
	
	// /* The budget slider 
	// ------------------------------------------------------ */
	// $( "#budget_slider" ).slider({
		// range: "min",
		// animate: true,
		// value: 1000,
		// min: 500,
		// max: 3000,
		// step: 500,
		// slide: function(event, ui) {
			// $("#budget").val("$" + ui.value);
		// }
	// });
				
	// $("#budget").val( "$" + $("#budget_slider").slider("value"));
	// $("#budget_slider").slider("pips", { rest: "label", prefix: "$", suffix: "" });
	// $("#budget_slider").slider("float", { prefix: "$", suffix: "", pips: true });
	
	// /* Show hide payment options
	// ------------------------------------------------------- */
	// $('.smartfm-ctrl').formShowHide();
			
});    
