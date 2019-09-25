{
    'name': 'AARSOL Activities',
    'summary': 'AARSOL Activities',
    'description': """
        AARSOL Activities:
        
        This module adds an activity board with form, tree, kanban, calendar, pivot, graph and search views.
        
        A smartButton of activities is added in the mail thread from form view.
        From this smartButton is linked to the activity board, to the view tree,
        which shows the activities related to the opportunity.

        From the form view of the activity you can navigate to the origin of the activity.
        
        ***********
        This module implements the capability to keep activities that have been completed, for future reporting, by setting them with the boolean 'Done'.
        The activities that have been completed will not appear in the chatter.
        """,
    'version': '12.0.1.0.0',
    'category': 'Accounts',
    'website': 'http://www.aarsol.com',
    'author': 'Farooq Arif',
    'license': 'AGPL-3',
    'depends': [
        'calendar',
        'board',
        'mail',
        'account'
    ],
    'data': [
        'data/activity_data.xml',
        'views/templates.xml',
        'views/mail_activity_view.xml',
        'views/account_payment_view.xml',
    ],
    'qweb': [
        'static/src/xml/inherit_chatter.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
