# -*- coding: utf-8 -*-
{
    'name' : 'Purchase Tracking',
    'version' : '1.0',
    'author': 'Mobilize (JLQC)',
    'summary': 'Purchase Tracking',
    'description': """
Manage Purchase Tracking
=========================
Agrega campos para seguimiento de compras
y confirmaciones de recepcion a clientes
    """,    
    'installable': True,
    'depends' : ['base', 'purchase','stock', 'delivery', 'sale_management'],
    'data': [
            'views/email_template_purchase_order.xml',
            'views/email_template_purchase_order_2.xml',
            'views/email_template_sale_order.xml',
            'views/email_template_stock_picking_in.xml',
            'views/email_template_stock_picking_out.xml',
		    'views/purchase_order.xml',
            'views/stock_picking.xml',
    ],
}
