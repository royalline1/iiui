
$(document).ready(function (e) {

var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
          content.style.maxHeight = null;
        } else {
          content.style.maxHeight = content.scrollHeight + "px";
        }
      });
    }

});


function changeProfile() {
        var change_apply_for = document.getElementById("change_in").value;
        var old_info= document.getElementById("old_info");
        var selected_field = document.getElementById("selected_field");
        if (change_apply_for.value!="") {
            selected_field.value= change_apply_for;

            odoo.define('odoocms_admission.onchange', function (require) {
                "use strict";
                var ajax = require('web.ajax');
                var core = require('web.core');
                var session = require('web.session');
                var base = require('web_editor.base');
                var _t = core._t;
                base.url_translations = '/website/translations';
                var _t = core._t;
                        $.ajax({
                            url: "/my/request/forms/search",
                            method: "POST",
                            dataType: "json",
                            data: {change_apply_for:change_apply_for},
                            success: function( data ) {
                                old_info.value= data.get_value;
                            },
                            error: function (error) {
                               alert('error: ' + error);
                            }
                        });
            });
        }
    }

function submitCourseRequest() {

        var com_subject_list = "";
        var elected_subject_list = "";
        var repeat_subject_list = "";
        var improve_subject_list = "";
        var subject_credit_hour = 0;

        // $('#is_same_address').is(":checked")

        var max_credit_hours = $('#max_credit_hours').val();
        $.each($('.com_subject_list'), function (index, value) {
            value = $(value)
            if (value.is(":checked")) {
                if (com_subject_list.length ==0){
                    com_subject_list+=value.val();

                }
                else {
                    com_subject_list+=","+value.val();
                }
            }
        });

        $.each($('.elected_subject_list'), function (index, value) {
            value = $(value)
            if (value.is(":checked")) {
                if (elected_subject_list.length ==0){
                    elected_subject_list+=value.val();
                }
                else {
                    elected_subject_list+=","+value.val();
                }

            }

        });

        $.each($('.repeat_subject_list'), function (index, value) {
            value = $(value)
            if (value.is(":checked")) {
                if (repeat_subject_list.length ==0){
                    repeat_subject_list+=value.val();
                    subject_credit_hour += parseFloat(value.attr("name"));
                }
                else {
                    repeat_subject_list+=","+value.val();
                    subject_credit_hour += parseFloat(value.attr("name"));
                }
            }

        });

        $.each($('.improve_subject_list'), function (index, value) {
            value = $(value)
            if (value.is(":checked")) {
                if (improve_subject_list.length ==0){
                    improve_subject_list+=value.val();
                    subject_credit_hour += parseFloat(value.attr("name"));
                }
                else {
                    improve_subject_list+=","+value.val();
                    subject_credit_hour += parseFloat(value.attr("name"));
                }
            }

        });
        if (improve_subject_list.length==0 & repeat_subject_list.length==0 & elected_subject_list.length==0 & com_subject_list.length==0 ){
            alert('No subject selected!');
        }
        else if (subject_credit_hour>max_credit_hours){
            alert("Maximum "+max_credit_hours+" Credit hours are allowed!");
        }
        else {
           $.ajax({
                url: "/my/request/course/enrollment/save",
                method: "POST",
                dataType: "json",
                data: {com_subject_list:com_subject_list,elected_subject_list:elected_subject_list,repeat_subject_list:repeat_subject_list,improve_subject_list:improve_subject_list,
                        subject_credit_hour:subject_credit_hour,},
                success: function (data) {
                    if (data.state == 'submit') {
                        alert("Submitted!")
                    }else if (data.state == 'nosubmit'){
                         alert("Can Update your request Now!")
                    }
                    else {
                       alert("Somethig went wong!")
                    }
                    window.location.href='/my/request/forms';
                },
                error: function (error) {
                    alert('error: ' + error);
                }
            });
        }

}
