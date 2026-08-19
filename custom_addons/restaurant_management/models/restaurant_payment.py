from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RestaurantPayment(models.Model):
    _name = 'restaurant.payment'
    _description = 'Restaurant Payment'

    order_id = fields.Many2one('restaurant.order',string='Order',required=True,ondelete='cascade')
    amount = fields.Monetary(string='Amount',required=True)
    currency_id = fields.Many2one('res.currency',string='Currency',required=True, default=lambda self: self.env.company.currency_id)
    payment_date = fields.Datetime(string='Payment Date',default=fields.Datetime.now,required=True)
    payment_method = fields.Selection(
        [
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('online', 'Online'),
            ('wallet', 'Wallet'),
        ],
        string='Payment Method',
        required=True,
    )

    @api.constrains('amount')
    def _check_amount(self):
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError(
                    'Payment amount must be greater than 0.'
                )

