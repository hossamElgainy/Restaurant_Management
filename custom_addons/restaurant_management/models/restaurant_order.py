from odoo import api, fields, models, tools
class RestaurantOrder(models.Model):
    _name = 'restaurant.order'

    order_no  = fields.Char(string='Order No',readonly=True,default='NEW',required=True,copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_restaurant_customer', '=', True)])
    waiter_id = fields.Many2one('res.users', string='Waiter')
    table_id = fields.Many2one('restaurant.table',string='Table')
    order_date = fields.Datetime(string='Order Date',default=fields.Datetime.now,readonly=True,copy=False)
    order_line_ids = fields.One2many('restaurant.order.line', 'order_id', string='Lines')
    total_amount = fields.Float(string='Total Amount',readonly=True, compute='_compute_total_amount',store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('order_no','NEW') =='NEW':
                val['order_no'] = self.env['ir.sequence'].next_by_code('restaurant.order') or 'NEW'
        return super().create(vals_list)

    @api.depends('order_line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount =sum(order.order_line_ids.mapped('subtotal'))