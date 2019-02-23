# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{'name': 'TH Withholding Tax Certificate',
 'version': '12.0.1.0.0',
 'author': 'Ecosoft,Odoo Community Association (OCA)',
 'website': '???',
 'license': 'AGPL-3',
 'category': 'Accounting',
 'depends': ['account',
             'l10n_it_withholding_tax',
             ],
 'data': ['security/ir.model.access.csv',
          'wizard/create_withholding_tax_cert.xml',
          'views/withholding_tax_cert.xml',
          'views/account_payment_view.xml'
          ],
 'installable': True,
 'development_status': 'alpha',
 'maintainers': ['kittiu'],
 }
