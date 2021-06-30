# -*- coding: utf-8 -*-
{
    'name' : 'AutoPro Dev',
    'version' : '1.0',
    'author': 'Mobilize (JLQC)',
    'category': 'Mobilize/Apps',
    'application': True,
    'summary': 'AutoPro Dev',
    'description': """
AutoPro Dev
=========================
Agrega personalizaciones para AutoPro
    """,    
    'depends' : ['base', 'purchase','stock', 'delivery', 'account', 'sale_management', 'eq_sale_advance_payment'],
    'data': [
            'views/email_template_purchase_order.xml',
            'views/email_template_purchase_order_2.xml',
            'views/email_template_sale_order.xml',
            'views/email_template_stock_picking_in.xml',
            'views/email_template_stock_picking_out.xml',
		    'views/purchase_order.xml',
            'views/sale_order.xml',
            'views/stock_picking.xml',
    ],
}
