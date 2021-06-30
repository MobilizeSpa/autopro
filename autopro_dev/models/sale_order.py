# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import date_utils
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tracking_purchase_order_ids = fields.One2many('purchase.order', 'tracking_sale_order_id', string='Ordenes de compra')
    tracking_purchase_order_count = fields.Integer(compute='_compute_tracking_counts')

    # ==== Payment widget fields ====
    invoice_outstanding_credits_debits_widget = fields.Text(groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_to_reconcile_info')
    invoice_has_outstanding = fields.Boolean(groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_to_reconcile_info')
    invoice_payments_widget = fields.Text(groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_reconciled_info')

    def _compute_payments_widget_to_reconcile_info(self):
        for rec in self:
            rec.invoice_outstanding_credits_debits_widget = json.dumps(False)
            rec.invoice_has_outstanding = False

            if rec.invoice_ids.state != 'posted' \
                    or rec.invoice_ids.payment_state not in ('not_paid', 'partial') \
                    or not rec.invoice_ids.is_invoice(include_receipts=True):
                continue

            pay_term_lines = rec.invoice_ids.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', rec.invoice_ids.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': rec.invoice_ids.id}

            if rec.invoice_ids.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == rec.invoice_ids.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = rec.invoice_ids.company_currency_id._convert(
                        abs(line.amount_residual),
                        rec.invoice_ids.currency_id,
                        rec.invoice_ids.company_id,
                        line.date,
                    )

                if rec.invoice_ids.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': rec.invoice_ids.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': rec.invoice_ids.currency_id.position,
                    'digits': [69, rec.invoice_ids.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })

            if not payments_widget_vals['content']:
                continue

            rec.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            rec.invoice_has_outstanding = True
    
    @api.depends('invoice_ids.move_type', 'invoice_ids.line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for rec in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if rec.invoice_ids.state == 'posted' and rec.invoice_ids.is_invoice(include_receipts=True):
                payments_widget_vals['content'] = rec.invoice_ids._get_reconciled_info_JSON_values()

            if payments_widget_vals['content']:
                rec.invoice_payments_widget = json.dumps(payments_widget_vals, default=date_utils.json_default)
            else:
                rec.invoice_payments_widget = json.dumps(False)

    @api.depends('tracking_purchase_order_ids')
    def _compute_tracking_counts(self):
        for rec in self:
            rec.tracking_purchase_order_count = len(rec.tracking_purchase_order_ids)

    def action_confirm(self):
        super(SaleOrder, self).action_confirm()

        po = self.env['purchase.order'].sudo().search([('state', '=', 'draft')], order='id desc')
        if po:
            po.tracking_sale_order_id = self.id
            po.button_confirm()

        # Este fragmento se deshabilitó a pedido del cliente
        # permite generar la factura de la orden de venta automáticamente y validarla

        #payment = self.env['sale.advance.payment.inv'].with_context(active_ids=self.ids).create({
        #    'advance_payment_method': 'delivered',
        #    'deduct_down_payments': True,
        #})
        #payment.create_invoices()
        #self.invoice_ids.action_post()

    def action_view_purchases(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('tracking_sale_order_id', '=', self.id)]
        return action