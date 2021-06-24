# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tracking_purchase_order_id = fields.Many2one('purchase.order')