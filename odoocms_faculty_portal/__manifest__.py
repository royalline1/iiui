# -*- coding: utf-8 -*-
{
    "name": "OdooCMS Faculty Portal",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Faculty Portal Module of OdooCMS""",
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'description': 'An easy and efficient management tool for Faculty Portal',
    

    # any module necessary for this one to work correctly
    'depends': ['portal','odoocms','odoocms_exam','odoocms_fee','odoocms_attendance','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/faculty_profile_templates.xml',
        'views/faculty_subjects_templates.xml',
        'views/faculty_class_students_templates.xml',
        'views/student_profile_templates.xml',
        'views/faculty_class_attendance_templates.xml',

        'views/assets.xml',
       
    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}