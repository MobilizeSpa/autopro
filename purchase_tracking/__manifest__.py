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
    'depends' : ['base','purchase','stock', 'delivery'],
    'data': [
            'views/email_template_stock_picking_in.xml',
		    'views/purchase_order.xml',
            'views/stock_picking.xml',
    ],
}
