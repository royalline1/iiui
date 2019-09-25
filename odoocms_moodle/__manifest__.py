# -*- coding: utf-8 -*-
{
    'name': "Moodle",
    'summary': 'Manage Moodle From Odoo.',
    'author': "Farooq",
    'website': "http://www.aarsol.com",    
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': ['odoocms'],

    'qweb': [
        #'static/src/xml/*.xml',
        #'views/templates.xml'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/moodle_menu.xml',
        #'views/tree_view_asset.xml',
        'views/categories_view.xml',
        'views/course_view.xml',
        'views/student_view.xml',
        
        
        'wizard/get_categories_view.xml',
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}
