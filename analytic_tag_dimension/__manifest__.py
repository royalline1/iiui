{
    "name": "Analytic Accounts Dimensions",
    'summary': "Group Analytic Entries by Dimensions",
    "version": "12.0",
    "license": "AGPL-3",
    "author": "AARSOL Team",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        'analytic',
        'account',
    ],
    "data": [
        'views/analytic_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": [
        'demo/analytic_demo.xml',
    ],
}
