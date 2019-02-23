# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Sales Invoice Plan",
    'version': "12.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    'website': "http://ecosoft.co.th",
    'category': "Sales",
    'license': "AGPL-3",
    'depends': ["sale",
                "account", ],
    'data': ["security/ir.model.access.csv",
             "wizard/sale_create_invoice_plan_view.xml",
             "wizard/sale_make_planned_invoice_view.xml",
             "views/sale_view.xml"],
    'installable': True,
}
