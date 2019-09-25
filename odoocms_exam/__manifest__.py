
{
    "name": "OdooCMS Exam",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Exam Management Module of OdooCMS""",
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'description': 'An easy way to handle the examinations in an educational '
                   'system with better reports and exam valuation and exam result '
                   'facilities',
    
    'depends': ['odoocms_registration'],
    'data': [
        'security/ir.model.access.csv',
        'security/odoocms_exam_security.xml',
        'menu/exam_menu_view.xml',
        'views/examination.xml',
        'views/exam_valuation.xml',
        'views/view_exam_activity.xml',
        #'views/exam_results.xml',
        'views/student_view.xml',
        'views/summary_view.xml',
        
        'wizard/report/odoocms_transcript_wizard_view.xml',
        'wizard/report/student_provisional_certificate_wiz_view.xml',
        'wizard/report/gpa_wise_student_wiz_view.xml',
        'wizard/report/semester_result_export_view.xml',
        'wizard/report/gpa_warning_wizard_view.xml',
        'wizard/report/student_exam_slip_wiz_view.xml',
        
        'reports/report.xml',
        'reports/student_provisional_certificate_report.xml',
        'reports/gpa_wise_student_report.xml',
        'reports/gpa_warning_report.xml',
        'reports/student_exam_slip_report.xml',
        
        
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
