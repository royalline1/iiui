function markall() {
    $( ".mark-attendance" ).prop( "checked", true );
    $("#mark_all_students_div").css("display", "none");
    $("#unmark_all_students_div").css("display", "block");
}

function unmarkall() {
    $( ".mark-attendance" ).prop( "checked", false );
    $("#mark_all_students_div").css("display", "block");
    $("#unmark_all_students_div").css("display", "none");
}


function save_attendance() {
  var student_list = [];
  $.each($('.mark-attendance'), function (index, value) {
        value = $(value);
        if (value.is(":checked")) {
            student_list.push(value.val());
        }
    });

    if(student_list.length>0) {
        var class_id = $("#student_class").val();
        student_ids=student_list[0];
        $.each(student_list, function( index, value ) {
            if(index>0){
                student_ids+=","+value;
            }
        });

        odoo.define('odoocms_faculty_portal.clickevent', function (require) {
                "use strict";
                var ajax = require('web.ajax');
                var core = require('web.core');
                var session = require('web.session');
                var base = require('web_editor.base');
                var _t = core._t;
                base.url_translations = '/website/translations';
                var _t = core._t;
                 $.ajax({
                            url: "/my/class/attendance/save",
                            method: "POST",
                            dataType: "json",
                            data: {class_id:class_id,student_ids:student_ids},
                            success: function( data ) {
                               alert("Sucessfully Added");
                            },
                            error: function (error) {
                               alert('error: ' + error);
                            }
                            });
                });
    }
    else{
        alert("Select Atleast One Student!")
    }

}