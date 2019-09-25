
{
    "name": "OdooCMS OBE",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Outcome Based Education Module of OdooCMS""",
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'depends': ['odoocms_registration','odoocms_exam'],
    'data': [
        'security/ir.model.access.csv',
        'security/odoocms_obe_security.xml',
        'menu/obe_menu_view.xml',
        
        'views/plo_clo_view.xml',
        'views/activity_view.xml',
        'views/obe_inherits_view.xml',
        'views/summary_view.xml',
        'views/obe_analysis_view.xml',
        'views/res_config_setting_view.xml',
        
        'wizard/exam_imports_view.xml',
        'wizard/activities_export_view.xml',
        'wizard/program_wise_plo_attainment_wiz_view.xml',
        'wizard/semester_wise_plo_attainment_wiz_view.xml',
        'wizard/obe_course_to_plo_mapping_wiz_view.xml',
        'wizard/obe_clo_to_plo_mapping_wiz_view.xml',
        'wizard/obe_class_clo_attainment_wiz_view.xml',



        'report/clo_attainment_report.xml',
        'report/program_wise_plo_attainment_report.xml',
        'report/semester_wise_plo_attainment_report.xml',
        'report/obe_student_transcript_report.xml',
        'report/obe_course_to_plo_mapping_report.xml',
        'report/obe_clo_to_plo_mapping_report.xml',
        'report/obe_class_clo_attainment_report.xml',
        'report/report.xml',
        

    ],

    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
