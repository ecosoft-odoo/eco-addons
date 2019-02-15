# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{'name': 'TH Accounting Reports',
 'version': '11.0.0.0.0',
 'author': 'Ecosoft,Odoo Community Association (OCA)',
 'website': '???',
 'license': 'AGPL-3',
 'category': 'Accounting',
 'depends': ['account',
             'account_move_tax_invoice',
             'excel_import_export',
             'date_range',
             'l10n_th_partner',
             ],
 'data': ['security/ir.model.access.csv',
          'views/menuitems.xml',
          'report_vat/report_vat.xml',
          'report_vat/templates.xml',
          ],
 'installable': True,
 'development_status': '???',
 'maintainers': ['kittiu'],
 }
