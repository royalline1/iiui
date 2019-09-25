# -*- encoding: utf-8 -*-
{
    'name': 'OdooCMS Entry Test',
    'summary': 'Online Entry Test Application.',
    'category': 'OdooCMS',
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 5,
    'author': 'AARSOL', 
    'company': 'AARSOL',
    'website': 'http://www.aarsol.com/',    
    'depends': ['website_partner', 'hr_recruitment', 'website_mail', 'website_form','website','odoocms_admission'],
	'data': [
		'security/ir.model.access.csv',
		
		'views/templates/assets.xml',
		'views/templates/entry_bank_fee.xml',
		'views/templates/registration_from.xml',
		'views/templates/registration_application_final_report.xml',
		'views/templates/registration_from_confirm.xml',
		'views/templates/admit_card.xml',
		
		'views/entrytest_view.xml',
		'views/entrytest_fee_center_view.xml',
		'views/application_view.xml',
		
    ],	
    'images': [		
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
