{
    "name": "OdooCMS Attendance",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Student Attendance Management Module of OdooCMS""",
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'description': 'An easy and efficient management tool to manage and track student'
                   ' attendance. Enables different types of filtration to generate '
                   'the adequate reports',
    
    'depends': ['odoocms','odoocms_registration'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_menu_view.xml',
        
        'views/students_attendance.xml',
        #'views/student_view.xml',
        
        'wizard/today_classes_view.xml',
        'wizard/short_attendance_warning_wizard_view.xml',
        
        'reports/short_attendance_warning_report.xml',
        'reports/report.xml',
        
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
