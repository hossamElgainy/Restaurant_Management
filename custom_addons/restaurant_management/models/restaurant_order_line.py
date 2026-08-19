from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantOrderLine(models.Model):
    _name = 'restaurant.order.line'
    _description = 'Restaurant Order Line'

    order_id = fields.Many2one(
        'restaurant.order',
        string='Order',
        required=True,
        ondelete='cascade',
    )

    item_id = fields.Many2one(
        'restaurant.menu.item',
        string='Item',
        required=True,
    )

    modifier_ids = fields.Many2many(
        'restaurant.menu.modifier',
        string='Modifiers',
    )

    # ---------------------------------------------------------
    # PRICES
    # ---------------------------------------------------------

    base_price = fields.Float(
        string='Base Price',
        readonly=True,
    )

    modifier_amount = fields.Float(
        string='Modifier Amount',
        readonly=True,
        compute='_compute_modifier_amount',
        store=True,
    )

    unit_price = fields.Float(
        string='Unit Price',
        readonly=True,
        compute='_compute_unit_price',
        store=True,
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
    )

    subtotal = fields.Float(
        string='Subtotal',
        readonly=True,
        compute='_compute_subtotal',
        store=True,
    )

    # ---------------------------------------------------------
    # MODIFIER AMOUNT
    # ---------------------------------------------------------

    @api.depends('modifier_ids', 'modifier_ids.price')
    def _compute_modifier_amount(self):
        for line in self:
            line.modifier_amount = sum(
                line.modifier_ids.mapped('price')
            )

    # ---------------------------------------------------------
    # UNIT PRICE
    # ---------------------------------------------------------

    @api.depends('base_price', 'modifier_amount')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = (
                line.base_price + line.modifier_amount
            )

    # ---------------------------------------------------------
    # SUBTOTAL
    # ---------------------------------------------------------

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (
                line.quantity * line.unit_price
            )

    # ---------------------------------------------------------
    # ITEM ONCHANGE
    # ---------------------------------------------------------

    @api.onchange('item_id')
    def _onchange_item_id(self):

        # When changing the item,
        # remove previously selected modifiers.
        self.modifier_ids = [(5, 0, 0)]

        if not self.item_id:

            self.base_price = 0.0

            return {
                'domain': {
                    'modifier_ids': []
                }
            }

        # The base price ALWAYS comes from the menu item.
        self.base_price = self.item_id.price

        return {
            'domain': {
                'modifier_ids': [
                    (
                        'id',
                        'in',
                        self.item_id.modifier_ids.ids,
                    )
                ]
            }
        }

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            item_id = vals.get('item_id')

            if item_id:

                item = self.env[
                    'restaurant.menu.item'
                ].browse(item_id)

                vals['base_price'] = item.price

        return super().create(vals_list)

    # ---------------------------------------------------------
    # WRITE
    # ---------------------------------------------------------

    def write(self, vals):

        if 'item_id' in vals:

            item = self.env[
                'restaurant.menu.item'
            ].browse(vals['item_id'])

            if item.exists():

                # Update only the base price.
                vals['base_price'] = item.price

                # Old modifiers belong to the old item.
                vals['modifier_ids'] = [
                    (5, 0, 0)
                ]

        return super().write(vals)

    # ---------------------------------------------------------
    # QUANTITY VALIDATION
    # ---------------------------------------------------------

    @api.constrains('quantity')
    def _check_quantity(self):

        for line in self:

            if line.quantity <= 0:

                raise ValidationError(
                    f'Quantity of {line.item_id.name} '
                    f'must be greater than 0.'
                )

    # ---------------------------------------------------------
    # MODIFIER VALIDATION
    # ---------------------------------------------------------

    @api.constrains('item_id', 'modifier_ids')
    def _check_modifiers(self):

        for line in self:

            if not line.item_id:
                continue

            invalid_modifiers = (
                line.modifier_ids
                - line.item_id.modifier_ids
            )

            if invalid_modifiers:

                raise ValidationError(
                    f'Some selected modifiers are not available '
                    f'for {line.item_id.name}.'
                )