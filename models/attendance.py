from odoo import api, fields, models
from odoo.exceptions import UserError


class WorkoutAttendance(models.Model):
    _name = 'workout.attendance'
    _description = 'Gym Attendance'
    _inherit = ['mail.thread']
    _order = 'check_in desc'
    member_id = fields.Many2one('res.partner', required=True, domain=[('is_workout_member', '=', True)], index=True)
    check_in = fields.Datetime(default=fields.Datetime.now, required=True, tracking=True)
    check_out = fields.Datetime(tracking=True)
    method = fields.Selection([('manual', 'Manual'), ('qr', 'QR'), ('rfid', 'RFID'), ('kiosk', 'Kiosk'), ('website', 'Website')], default='manual', required=True)
    session_id = fields.Many2one('workout.session', ondelete='set null')
    state = fields.Selection([('checked_in', 'Checked In'), ('checked_out', 'Checked Out')], default='checked_in', compute='_compute_state', store=True)

    @api.depends('check_out')
    def _compute_state(self):
        for record in self: record.state = 'checked_out' if record.check_out else 'checked_in'

    def action_check_out(self):
        if any(record.check_out for record in self): raise UserError('This attendance has already been checked out.')
        self.write({'check_out': fields.Datetime.now()})
