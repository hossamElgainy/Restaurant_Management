from odoo import fields, models

class RestaurantCustomer(models.Model):
    _description = 'Restaurant Customer'
    _inherit = 'res.partner'

    is_restaurant_customer = fields.Boolean(default=False)

    order_ids = fields.One2many(
        'restaurant.order',
        'customer_id',string='Orders')