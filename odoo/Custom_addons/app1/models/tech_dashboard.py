from odoo import models, fields, api, _ , tools


class technicalOfficeProjectFollowUp(models.Model):
    _name = 'technical.office.followup'
    _description = 'Project Follow Up'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('technical.office.project', string='Project', required=True)
    panel_id = fields.Char(related='project_id.panel_ids.name', string='Panel', required=True)
    product_id = fields.Many2one('inventory.product', string='Product', required=True)
    quantity_needed = fields.Integer(string='Quantity' , compute='_compute_quantity_needed')

    @api.depends('product_id')
    def _compute_quantity_needed(self):
        for followup in self:
            # Get the installed quantity from the BOM
            installed_qty = self.env['technical.office.project.bom'].search([
                ('inventory_product_id', '=', followup.product_id.id),
                ('panel_id', '=', followup.panel_id)
            ], limit=1).installed_qty
            # check if the installed quantity is not found

            # Get the current stock quantity
            current_stock_qty = self.env['inventory.product'].search([
                ('id', '=', followup.product_id.id)
            ], limit=1).current_stock_qty
            # Calculate the quantity needed
            followup.quantity_needed = installed_qty - current_stock_qty
            # Check if the quantity needed is less than or equal to 0
            if followup.quantity_needed <= 0:
                followup.quantity_needed = 0
            return followup.quantity_needed

class TechnicalOfficePanelPhaseHistory(models.Model):
    _name = 'technical.office.panel.phase.history'
    _description = 'Panel Phase History'
    _order = 'start_date desc'
    
    panel_id = fields.Many2one('technical.office.project.panel', string='Panel', required=True, ondelete='cascade')
    project_id = fields.Char(related='panel_id.project_id.name', string='Project', store=True, readonly=True)
    phase = fields.Selection([
        ('studying', 'Studying'),
        ('waiting_approval', 'Waiting for Manufacturing Approval'),
        ('manufacture_queue', 'In Manufacture Queue'),
        ('bend_phase', 'In Bend Phase'),
        ('painting', 'In Painting'),
        ('assembly', 'Assembly'),
        ('copper_formation', 'Copper Formation'),
        ('classic_control', 'Classic Control and Automation'),
        ('quality_control', 'Quality Control'),
        ('to_be_exported', 'To Be Exported'),
        ('completed', 'Completed')
    ], string='Phase', required=True)
    
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date')
    duration = fields.Float(string='Duration (Days)', compute='_compute_duration', store=True)
    user_id = fields.Many2one('res.users', string='Changed By', required=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration = delta.total_seconds() / 86400  # Convert to days
            else:
                record.duration = 0

class TechnicalOfficePanelDashboard(models.Model):
    _name = 'technical.office.panel.dashboard'
    _description = 'Panel Dashboard'
    _auto = False
    
    phase = fields.Selection([
        ('studying', 'Studying'),
        ('waiting_approval', 'Waiting for Manufacturing Approval'),
        ('manufacture_queue', 'In Manufacture Queue'),
        ('bend_phase', 'In Bend Phase'),
        ('painting', 'In Painting'),
        ('assembly', 'Assembly'),
        ('copper_formation', 'Copper Formation'),
        ('classic_control', 'Classic Control and Automation'),
        ('quality_control', 'Quality Control'),
        ('to_be_exported', 'To Be Exported'),
        ('completed', 'Completed')
    ], string='Phase')
    
    panel_count = fields.Integer(string='Panel Count')
    avg_duration = fields.Float(string='Average Duration (Days)')
    project_name = fields.Char(string='Project')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT 
                    row_number() OVER () AS id,
                    p.phase,
                    COUNT(p.id) as panel_count,
                    AVG(CASE 
                        WHEN p.phase_start_date IS NOT NULL 
                        THEN EXTRACT(epoch FROM (CURRENT_TIMESTAMP - p.phase_start_date)) / 86400 
                        ELSE 0 
                    END) as avg_duration,
                    pr.name as project_name
                FROM technical_office_project_panel p
                JOIN technical_office_project pr ON p.project_id = pr.id
                GROUP BY p.phase, pr.name
            )
        """ % self._table)