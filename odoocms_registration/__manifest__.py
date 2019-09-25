
{
    "name": "OdooCMS Registration",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Registration Management Module of OdooCMS",
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    "depends": ['odoocms'],
    "data": [
        'security/ir.model.access.csv',
        'security/odoocms_registration_security.xml',
        
        'menu/registration_menu_view.xml',
        
        'views/batch_section_view.xml',
        'views/semester_scheme_view.xml',
        'views/class_view.xml',
        'views/subject_registration_view.xml',
        'views/student_registration_view.xml',
        'views/student_view.xml',
        'views/student_request_view.xml',
        
        'wizard/register_scheme_course_view.xml',
    ],
    'images': ['static/description/banner.jpg'],
    "installable": True,
    "auto_install": False,
    'application': True,
}
