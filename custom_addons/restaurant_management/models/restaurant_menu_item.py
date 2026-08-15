from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class RestaurantMenuItem(models.Model):
    _name = 'restaurant.menu.item'
    _description = 'Restaurant Menu Item'

    name = fields.Char(required=True)
    category_id = fields.Many2one('restaurant.menu.category',string='Category',required=True)
    price = fields.Float(required=True)
    description = fields.Text()
    image = fields.Binary()
    available = fields.Boolean(default=True)


    @api.constrains('price')
    def _check_price(self):
        for item in self:
            if item.price <= 0:
                raise ValidationError('Price must be greater than 0')