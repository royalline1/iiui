# -*- encoding: utf-8 -*-
{
    'name': 'OdooCMS Admission Online',
    'summary': 'Online Admission Application.',
    'category': 'OdooCMS',
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 4,
    'author': 'AARSOL', 
    'company': 'AARSOL',
    'website': 'http://www.aarsol.com/',    
    'depends': ['website_partner', 'website_mail', 'website_form','odoocms_admission','website','base_setup','auth_signup',],
	'data': [
		'security/ir.model.access.csv',
		
		'views/templates/assets.xml',
		'views/templates/registration_from.xml',
		'views/templates/registration_from_submit.xml',
		'views/templates/registration_application_final_report.xml',
		'views/templates/admission_bank_fee.xml',
		'views/templates/signup_form.xml',
		'views/templates/portal_template.xml',
		
		
		'views/res_config_settings_views.xml',
		'views/entrytest_view.xml',
		
    ],	
    'images': [		
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
