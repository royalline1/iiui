# -*- coding: utf-8 -*-

{
    'name': "OdooCMS Admission",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Admission Module of Educational""",
    'author': 'AARSOL', 
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'depends': ['odoocms'],   # 'utm','website_mail','website_partner','mail','website_form','website'
    'data': [
        'security/ir.model.access.csv',
        'security/odoocms_admission_security.xml',
        
        'views/sequence.xml',
        'menus/odoocms_admission_menu.xml',
        
        'wizard/application_reject_view.xml',
        'wizard/non_subsidized_form_wizard_view.xml',
        'wizard/odoocms_merit_register_wizard_view.xml',
        'wizard/odoocms_merit_status_view.xml',
        'wizard/odoocms_close_register_wizard_view.xml',
        
        'wizard/report/odoocms_preference_wizard_view.xml',
        'wizard/report/odoocms_meritlist_report_wizard_view.xml',
        'wizard/report/odoocms_merit_interview_wizard_view.xml',
        'wizard/report/odoocms_final_merit_list_wizard_view.xml',

        'views/admission_register_view.xml',
        'views/odoocms_admission_quota.xml',
        'views/odoocms_application_view.xml',
        'views/documents_view.xml',
        'views/odoocms_merit_list.xml',
        'views/odoocms_admission_common.xml',

        'reports/student_preference_report.xml',
        'reports/non_subsidized_form_report.xml',
        'reports/student_meritlist_report.xml',
        'reports/student_merit_interview_report.xml',
        'reports/student_final_merit_list_report.xml',
        'reports/report.xml',
        
        
        
        
        
        
        
        #'views/admission_template.xml',
        #'views/portal_templates.xml',
        
        
        
        
        
    



        
    ],
    'demo': [
        # 'demo/admission_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
