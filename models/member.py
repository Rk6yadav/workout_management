from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_workout_member = fields.Boolean(string='Fitness Member', index=True)
    member_reference = fields.Char(string='Member ID', copy=False, readonly=True, index=True)
    date_of_birth = fields.Date()
    gender = fields.Selection([('female', 'Female'), ('male', 'Male'), ('other', 'Other'), ('undisclosed', 'Prefer not to say')])
    height_cm = fields.Float(string='Height (cm)', digits=(6, 2))
    fitness_level = fields.Selection([('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner')
    preferred_workout_time = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('flexible', 'Flexible')], default='flexible')
    trainer_id = fields.Many2one('res.partner', domain=[('is_workout_trainer', '=', True)], ondelete='set null')
    is_workout_trainer = fields.Boolean(string='Personal Trainer', index=True)
    joining_date = fields.Date(default=fields.Date.today)
    emergency_contact_name = fields.Char()
    emergency_contact_phone = fields.Char()
    fitness_notes = fields.Text(help='Fitness programming notes. Do not use this field for medical diagnosis.')
    dietary_preferences = fields.Text()
    allergy_notes = fields.Text()
    goal_ids = fields.One2many('workout.goal', 'member_id')
    measurement_ids = fields.One2many('workout.measurement', 'member_id')
    session_ids = fields.One2many('workout.session', 'member_id')
    membership_ids = fields.One2many('workout.membership', 'member_id')
    current_weight_kg = fields.Float(compute='_compute_current_measurement', string='Current Weight (kg)', digits=(6, 2))
    body_fat_percent = fields.Float(compute='_compute_current_measurement', string='Body Fat %', digits=(5, 2))
    active_membership_id = fields.Many2one('workout.membership', compute='_compute_active_membership')
    membership_status = fields.Selection(related='active_membership_id.status', string='Membership Status')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_workout_member') and not vals.get('member_reference'):
                vals['member_reference'] = self.env['ir.sequence'].next_by_code('workout.member') or 'New'
        return super().create(vals_list)

    def _compute_current_measurement(self):
        Measurement = self.env['workout.measurement']
        for member in self:
            latest = Measurement.search([('member_id', '=', member.id)], order='measurement_date desc, id desc', limit=1)
            member.current_weight_kg = latest.weight_kg if latest else 0.0
            member.body_fat_percent = latest.body_fat_percent if latest else 0.0

    def _compute_active_membership(self):
        today = fields.Date.today()
        for member in self:
            member.active_membership_id = self.env['workout.membership'].search([
                ('member_id', '=', member.id), ('status', '=', 'active'),
                ('start_date', '<=', today), ('end_date', '>=', today),
            ], order='end_date desc', limit=1)
