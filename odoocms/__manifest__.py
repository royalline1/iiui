
{
    'name': 'OdooCMS Core',
    'version': '12.0.1.0.1',
    'summary': """Core Module of Institutes""",
    'description': 'Core Module of Educational Institutes',
    'category': 'OdooCMS',
    'sequence': 2,
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'depends': ['base', 'mail','hr','website'],
    'data': [
        'security/odoocms_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_setting_view.xml',
        'views/odoocms_menu.xml',
        # 'views/assets.xml',
        
        'views/academic_view.xml',
        'views/amenities_view.xml',
        'views/campus_view.xml',
        'views/faculty_view.xml',
        
        'views/subject_view.xml',
        'views/department_view.xml',
        'views/program_view.xml',
        'views/study_scheme_view.xml',
        
        'views/faculty_staff_view.xml',
        'views/student_view.xml',

        'wizard/change_student_state_view.xml',
        'views/sequence.xml',
        'data/data.xml',
       
    ],    
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
