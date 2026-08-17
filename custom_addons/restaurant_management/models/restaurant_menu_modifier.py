from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RestaurantMenuModifier(models.Model):
    _name = 'restaurant.menu.modifier'
    _description = 'Restaurant Menu Modifier'

    name = fields.Char(string='Modifier Name',required=True)
    price = fields.Float(required=True)
    available = fields.Boolean(default=True)
    item_ids = fields.Many2many(
        'restaurant.menu.item',
        'restaurant_menu_item_modifier_rel',
        'modifier_id',
        'item_id',
        string='Menu Items'
    )
    @api.constrains('price')
    def _check_price(self):
        for menu_item in self:
            if menu_item.price and menu_item.price <0:
                raise ValidationError("Price Must Have A Zero For Free Modifiers Or Positive Value")