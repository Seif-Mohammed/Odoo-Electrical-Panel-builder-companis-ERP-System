from odoo import models, fields, api
import json
from datetime import datetime, timedelta

class PlcData(models.Model):
    _name = 'plc.data'
    _description = 'PLC Data Log'
    _order = 'timestamp desc'

    name = fields.Char('Reference', default=lambda self: self._default_name())
    plc_ip = fields.Char('PLC IP Address', required=True)
    plc_rack = fields.Integer('PLC Rack', default=0)
    plc_slot = fields.Integer('PLC Slot', default=1)
    timestamp = fields.Datetime('Timestamp', required=True)
    
    # Input/Output data
    input_data = fields.Text('Input States (JSON)')
    output_data = fields.Text('Output States (JSON)')
    raw_data = fields.Text('Raw Data')
    
    # Parsed statistics
    active_inputs = fields.Integer('Active Inputs', default=0)
    active_outputs = fields.Integer('Active Outputs', default=0)
    total_inputs = fields.Integer('Total Inputs', default=0)
    total_outputs = fields.Integer('Total Outputs', default=0)
    
    # API info
    api_key = fields.Char('API Key')
    
    # Computed fields
    input_activity_rate = fields.Float('Input Activity %', compute='_compute_activity_rates', store=True)
    output_activity_rate = fields.Float('Output Activity %', compute='_compute_activity_rates', store=True)
    
    # Status field
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error')
    ], string='Status', compute='_compute_status', store=True)

    def _default_name(self):
        return f"PLC Data {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    @api.depends('active_inputs', 'total_inputs', 'active_outputs', 'total_outputs')
    def _compute_activity_rates(self):
        for record in self:
            record.input_activity_rate = (record.active_inputs / record.total_inputs * 100) if record.total_inputs > 0 else 0
            record.output_activity_rate = (record.active_outputs / record.total_outputs * 100) if record.total_outputs > 0 else 0

    @api.depends('timestamp')
    def _compute_status(self):
        for record in self:
            if record.timestamp:
                time_diff = datetime.now() - record.timestamp
                if time_diff.total_seconds() < 300:  # 5 minutes
                    record.status = 'online'
                elif time_diff.total_seconds() < 3600:  # 1 hour
                    record.status = 'offline'
                else:
                    record.status = 'error'
            else:
                record.status = 'error'

    def get_parsed_inputs(self):
        """Return parsed input data as dictionary"""
        if self.input_data:
            try:
                return json.loads(self.input_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def get_parsed_outputs(self):
        """Return parsed output data as dictionary"""
        if self.output_data:
            try:
                return json.loads(self.output_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def get_input_states(self):
        """Return formatted input states for display"""
        inputs = self.get_parsed_inputs()
        return [(key, 'ON' if value == 1 else 'OFF') for key, value in inputs.items()]

    def get_output_states(self):
        """Return formatted output states for display"""
        outputs = self.get_parsed_outputs()
        return [(key, 'ON' if value == 1 else 'OFF') for key, value in outputs.items()]

    @api.model
    def get_latest_plc_data(self, plc_ip=None):
        """Get latest PLC data, optionally filtered by IP"""
        domain = []
        if plc_ip:
            domain.append(('plc_ip', '=', plc_ip))
        
        return self.search(domain, order='timestamp desc', limit=1)

    @api.model
    def cleanup_old_data(self, days=30):
        """Clean up old PLC data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_records = self.search([('timestamp', '<', cutoff_date)])
        old_records.unlink()
        return len(old_records)