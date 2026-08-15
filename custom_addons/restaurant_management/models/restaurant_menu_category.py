from odoo import api, fields, models, tools
class RestaurantMenuCategory(models.Model):
    _name = 'restaurant.menu.category'
    _description = 'Restaurant Menu Category'
    name = fields.Char(required=True)
    item_ids = fields.One2many('restaurant.menu.item', 'category_id',string="Items")