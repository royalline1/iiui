odoo.define('odoocms_moodle.form_view_header', function(require){
    'use strict';
    var core = require('web.core');
    var FormView = require('web.FormView');
    var form_common = require('web.form_common');
    var Qweb = core.qweb;

    FormView.include({
        render_buttons: function($node){
            this._super($node);
            this.$buttons.find('.o_form_button_save').click(this.proxy('save_button_override'));            
        },

        save_button_override: function(){
            if (this.model=='odoocms.moodle.course'){
                var Model = require('web.Model');
                var custom_model = new Model('odoocms.moodle.course');
                //custom_model.call('create_course');
            }
            else{
                //alert(this.model);
                if (this.model=='moodle.category'){
                    var Model = require('web.Model');
                    var custom_model = new Model('odoocms.moodle.category');
                    //custom_model.call('create_category', {});
                }      
            }            
        }
    });

});