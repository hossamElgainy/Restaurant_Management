from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantReservation(models.Model):
    _name = 'restaurant.reservation'
    _description = 'Restaurant Reservation'

    customer_id = fields.Many2one('res.partner',string='Customer',domain=[('is_restaurant_customer', '=', True)],required=True)

    guests = fields.Integer(string='Number of Guests',required=True)

    table_id = fields.Many2one('restaurant.table',string='Table',required=True)

    reservation_date = fields.Date(string='Date of Reservation',required=True)

    start_datetime = fields.Datetime(string='Start Time',required=True)

    end_datetime = fields.Datetime(string='End Time',required=True)

    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='pending',
        required=True,
    )

    def action_pending(self):
        for reservation in self:
            reservation.state = 'pending'

    def action_confirmed(self):
        for reservation in self:

            if reservation.state != 'pending':
                raise ValidationError(
                    "Could only confirm a pending reservation."
                )

            reservation._check_reservation_values()
            reservation._check_table_availability()

            reservation.state = 'confirmed'

    def action_cancelled(self):
        for reservation in self:
            if reservation.state == 'cancelled':
                continue

            reservation.state = 'cancelled'


    @api.constrains(
        'guests',
        'table_id',
        'start_datetime',
        'end_datetime',
        'state',
    )
    def _check_reservation(self):
        for reservation in self:

            if reservation.state != 'confirmed':
                continue

            reservation._check_reservation_values()
            reservation._check_table_availability()

    def _check_reservation_values(self):

        for reservation in self:

            if not reservation.customer_id:
                raise ValidationError(
                    "Please select a customer."
                )

            if not reservation.guests or reservation.guests <= 0:
                raise ValidationError(
                    "Number of guests must be greater than zero."
                )

            if not reservation.reservation_date:
                raise ValidationError(
                    "Please select a reservation date."
                )

            if not reservation.start_datetime:
                raise ValidationError(
                    "Please select a start time."
                )

            if not reservation.end_datetime:
                raise ValidationError(
                    "Please select an end time."
                )

            if reservation.start_datetime >= reservation.end_datetime:
                raise ValidationError(
                    "End time must be after start time."
                )

            if reservation.start_datetime.date() != reservation.reservation_date:
                raise ValidationError(
                    "Start time must belong to the reservation date."
                )

            if reservation.end_datetime.date() != reservation.reservation_date:
                raise ValidationError(
                    "End time must belong to the reservation date."
                )

    def _check_table_availability(self):
        for reservation in self:
            if not reservation.table_id:
                raise ValidationError(
                    "Please select a table."
                )

            if reservation.table_id.capacity < reservation.guests:
                raise ValidationError(
                    "The selected table does not have enough capacity "
                    "for the number of guests."
                )


            overlapping_reservations = self.search([
                ('id', '!=', reservation.id),
                ('table_id', '=', reservation.table_id.id),
                ('state', '=', 'confirmed'),
                ('start_datetime', '<', reservation.end_datetime),
                ('end_datetime', '>', reservation.start_datetime),
            ])

            if overlapping_reservations:
                raise ValidationError(
                    "This table is already reserved during this time."
                )

    @api.onchange('reservation_date')
    def _onchange_reservation_date(self):
        if self.reservation_date:

            current_time = (
                self.start_datetime.time()
                if self.start_datetime
                else datetime.now().time()
            )

            self.start_datetime = datetime.combine(
                self.reservation_date,
                current_time,
            )

        else:
            self.start_datetime = False

    @api.onchange('start_datetime')
    def _onchange_start_datetime(self):
        if self.start_datetime:
            self.end_datetime = self.start_datetime
        else:
            self.end_datetime = False

    @api.onchange(
        'reservation_date',
        'start_datetime',
        'end_datetime',
    )
    def _onchange_available_tables(self):

        if not self.start_datetime or not self.end_datetime:
            return

        reservation_domain = [
            ('state', '=', 'confirmed'),
            ('start_datetime', '<', self.end_datetime),
            ('end_datetime', '>', self.start_datetime),
        ]

        if self._origin.id:
            reservation_domain.append(
                ('id', '!=', self._origin.id)
            )

        overlapping_reservations = self.env[
            'restaurant.reservation'
        ].search(reservation_domain)

        reserved_table_ids = overlapping_reservations.mapped(
            'table_id'
        ).ids

        if reserved_table_ids:
            return {
                'domain': {
                    'table_id': [
                        ('id', 'not in', reserved_table_ids),
                    ],
                },
            }

        return {
            'domain': {
                'table_id': [],
            },
        }