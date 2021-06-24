# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # purchase_tracking_factory = fields.Char('Tracking de fabrica')
    # purchase_tracking_carrier = fields.Char('Tracking de transportista internacional')
    tracking_sale_order_ids = fields.One2many('sale.order', 'tracking_purchase_order_id', string='Pedidos de venta')

    def send_message(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('purchase_tracking', 'email_template_tracking_purchase_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment'
        })

        return {
            'name': _('Redactar Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

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
                m = '<li>{0} - cant. {1}'.format(line.name, line.product_qty)
                message += m + (' (con tracking de fabrica {0})'.format(line.purchase_tracking_factory) if line.purchase_tracking_factory else '') + (' (con tracking de fabrica {0})'.format(line.purchase_tracking_carrier) if line.purchase_tracking_carrier else '')
            message += '</ul>'

            self.message_post(body=message, subject=self.name, message_type='email', subtype_xmlid="mail.mt_comment")
            if self.picking_ids:
                self.picking_ids.message_post(body=message)
        
        return res 
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_tracking_factory = fields.Char('Tracking de fabrica')
    purchase_tracking_carrier = fields.Char('Tracking de transportista')
    