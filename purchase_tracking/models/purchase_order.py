# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_tracking_factory = fields.Char('Tracking de fabrica')
    purchase_tracking_carrier = fields.Char('Tracking de transportista internacional')

    def write(self, vals):
        message = False

        if 'order_line' in vals:
            for line in vals['order_line']:
                if line[0] in [0,1] and (line[2].get('purchase_tracking_factory', False) or line[2].get('purchase_tracking_carrier', False)):
                    message = True
                
        res = super(PurchaseOrder, self).write(vals)

        if message:
            message = '<b>La orden nro: {0}</b> ha sido actualizado. Con detalle:<br/><ul>'.format(self.name)
            for line in self.order_line:
                message += '<li>{0} - cant. {1} (con tracking de fabrica {2}, y tracking de transportista {3})</li>'.format(line.name, line.product_qty, line.purchase_tracking_factory, line.purchase_tracking_carrier)
            message += '</ul>'

            self.message_post(body=message, subject=self.name, message_type='email', subtype_xmlid="mail.mt_comment")
            if self.picking_ids:
                self.picking_ids.message_post(body=message)
        
        return res 
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_tracking_factory = fields.Char('Tracking de fabrica')
    purchase_tracking_carrier = fields.Char('Tracking de transportista')
    