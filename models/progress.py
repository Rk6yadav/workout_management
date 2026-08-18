from odoo import api, fields, models


class WorkoutGoal(models.Model):
    _name = 'workout.goal'
    _description = 'Fitness Goal'
    _order = 'target_date, id'
    name = fields.Char(required=True)
    member_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    goal_type = fields.Selection([('weight', 'Weight'), ('body_fat', 'Body Fat'), ('strength', 'Strength'), ('endurance', 'Endurance'), ('consistency', 'Consistency'), ('custom', 'Custom')], required=True)
    start_value = fields.Float(digits=(10, 2))
    current_value = fields.Float(digits=(10, 2))
    target_value = fields.Float(required=True, digits=(10, 2))
    unit = fields.Char(required=True, default='kg')
    start_date = fields.Date(default=fields.Date.today, required=True)
    target_date = fields.Date()
    status = fields.Selection([('active', 'Active'), ('achieved', 'Achieved'), ('cancelled', 'Cancelled')], default='active')
    progress_percent = fields.Float(compute='_compute_progress', digits=(5, 2))

    @api.depends('start_value', 'current_value', 'target_value')
    def _compute_progress(self):
        for record in self:
            span = record.target_value - record.start_value
            record.progress_percent = min(100, max(0, ((record.current_value - record.start_value) / span * 100))) if span else 0


class WorkoutMeasurement(models.Model):
    _name = 'workout.measurement'
    _description = 'Body Measurement'
    _order = 'measurement_date desc, id desc'
    member_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    measurement_date = fields.Date(default=fields.Date.today, required=True)
    weight_kg = fields.Float(string='Weight (kg)', digits=(6, 2))
    body_fat_percent = fields.Float(string='Body Fat %', digits=(5, 2))
    bmi = fields.Float(compute='_compute_bmi', store=True, digits=(5, 2))
    chest_cm = fields.Float(string='Chest (cm)', digits=(6, 2))
    waist_cm = fields.Float(string='Waist (cm)', digits=(6, 2))
    hip_cm = fields.Float(string='Hip (cm)', digits=(6, 2))
    notes = fields.Text()

    @api.depends('weight_kg', 'member_id.height_cm')
    def _compute_bmi(self):
        for record in self:
            height_m = record.member_id.height_cm / 100
            record.bmi = record.weight_kg / (height_m ** 2) if height_m and record.weight_kg else 0


class WorkoutPersonalRecord(models.Model):
    _name = 'workout.personal.record'
    _description = 'Personal Record'
    _order = 'achieved_on desc, id desc'
    member_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    exercise_id = fields.Many2one('workout.exercise', required=True, ondelete='cascade')
    record_type = fields.Selection([('max_weight', 'Maximum Weight'), ('max_volume', 'Maximum Volume'), ('max_reps', 'Maximum Repetitions')], required=True)
    value = fields.Float(required=True, digits=(10, 2))
    unit = fields.Char(required=True)
    achieved_on = fields.Date(default=fields.Date.today, required=True)
    session_id = fields.Many2one('workout.session', ondelete='set null')
    _sql_constraints = [('workout_pr_unique', 'unique(member_id, exercise_id, record_type)', 'Only one current personal record is allowed per member, exercise, and record type.')]


class WorkoutProgressEvent(models.Model):
    _name = 'workout.progress.event'
    _description = 'Workout Progress Event'
    member_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    session_id = fields.Many2one('workout.session', required=True, ondelete='cascade')
    event_date = fields.Datetime(default=fields.Datetime.now)
    total_volume_kg = fields.Float()
    pr_count = fields.Integer()

    @api.model
    def create_from_session(self, session):
        pr_count = 0
        for executed in session.session_exercise_ids:
            completed = executed.set_ids.filtered('completed')
            if not completed: continue
            candidates = [('max_weight', max(completed.mapped('weight_kg')), 'kg'), ('max_reps', max(completed.mapped('reps')), 'reps'), ('max_volume', sum(completed.mapped('volume_kg')), 'kg')]
            for record_type, value, unit in candidates:
                existing = self.env['workout.personal.record'].search([('member_id', '=', session.member_id.id), ('exercise_id', '=', executed.exercise_id.id), ('record_type', '=', record_type)], limit=1)
                if not existing or value > existing.value:
                    vals = {'member_id': session.member_id.id, 'exercise_id': executed.exercise_id.id, 'record_type': record_type, 'value': value, 'unit': unit, 'achieved_on': fields.Date.today(), 'session_id': session.id}
                    if existing: existing.write(vals)
                    else: self.env['workout.personal.record'].create(vals)
                    pr_count += 1
        return self.create({'member_id': session.member_id.id, 'session_id': session.id, 'total_volume_kg': session.total_volume_kg, 'pr_count': pr_count})
