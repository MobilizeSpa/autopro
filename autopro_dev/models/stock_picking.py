# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tracking_purchase_order = fields.Many2one('purchase.order', compute='_compute_tracking_order')
    tracking_sale_order = fields.Many2one('sale.order', compute='_compute_tracking_order')

    def _compute_tracking_order(self):
        for rec in self:
            rec.tracking_purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
            rec.tracking_sale_order = self.env['sale.order'].search([('name','=',self.origin)])

    def send_message_in(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('autopro_dev', 'email_template_stock_picking_in')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'stock.picking',
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

    def send_message_out(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('autopro_dev', 'email_template_stock_picking_out')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'stock.picking',
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

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.picking_type_code == 'outgoing' and rec.tracking_sale_order:
                total_paid = 0
                payments = self.env['account.payment'].search([('ref','=',rec.origin)])
                for payment in payments:
                    total_paid += payment.amount
                if rec.tracking_sale_order.amount_total > total_paid:
                    raise exceptions.ValidationError(_('El pedido de venta relacionado aún no ha sido pagado en totalidad, por lo que no puede completar esta entrega'))
        return res
