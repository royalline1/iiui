 odoo.define('odoocms_moodle.tree_view_header', function(require){
    "use strict";

    var core = require('web.core');
    var ListView  = require('web.ListView');
    var Qweb = core.qweb;

    ListView.include({
        render_buttons: function($node){
            var self = this;
            this._super($node);
            this.$buttons.find('.o_refresh_category').click(self.proxy('refresh_category'));
            this.$buttons.find('.o_refresh_course').click(self.proxy('refresh_course'));
            this.$buttons.find('.o_list_button_add').click(self.proxy('create_button'));
        },
        
        refresh_category: function(){
            var Model = require('web.Model');
            var custom_model = new Model('odoocms.moodle.category');
            custom_model.call('get_categories');

        },

        refresh_course: function(){
            // since a course depends on a category when refreshing the list of courses,
            // We automatically have to refresh the category list first
            var Model = require('web.Model');
            var category_model = new Model('odoocms.moodle.category');
            category_model.call('get_categories');
            var course_model = new Model('odoocms.moodle.course');
            course_model.call('get_courses');
        },

        create_button: function(){
            if (this.model=='odoocms.moodle.category'){
                var Model = require('web.Model');
                var category_model = new Model('odoocms.moodle.category');
                //category_model.call('fetch_category');

            }
        }
    });

});
