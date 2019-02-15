# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{'name': 'Thai PND Reports',
 'version': '11.0.0.0.0',
 'author': 'Ecosoft,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Accounting',
 'depends': ['excel_import_export',
             'date_range',
             'l10n_th_partner',
             'l10n_th_withholding_tax_cert'],
 'data': ['report_pnd/report_pnd.xml',
          'report_pnd/templates.xml',
          ],
 'installable': True,
 # 'development_status': 'Mature',
 # 'maintainers': ['guewen'],
 }
