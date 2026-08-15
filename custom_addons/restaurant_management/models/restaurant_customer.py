from odoo import api, fields, models, tools

class RestaurantCustomer(models.Model):
    _description = 'Restaurant Customer'
    _inherit = 'res.partner'

    is_restaurant_customer = fields.Boolean(default=False)