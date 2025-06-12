from odoo import models, fields, api, _ 


class technicalOfficeProject(models.Model):
    _name = 'technical.office.project'
    _description = 'Technical Office Projects'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Project Name', required=True)
    project_sn = fields.Char(string='ID/SN', required=True)
    version_no = fields.Char(string='Version Number')
    
    # Client Information
    brand = fields.Char(string='Brand')
    client = fields.Char(string='Client')
    consultant = fields.Char(string='Consultant')
    owner = fields.Char(string='Owner')
    
    # Project Team
    tech_support = fields.Many2one('res.users', string='Technical Support')
    sales_eng = fields.Many2one('res.users', string='Sales Engineer')
    
    # Project Dates
    start_date = fields.Date(string='Project Start Date')
    due_date = fields.Date(string='Due Date')
    last_activated = fields.Date(string='Last Activated')
    finished = fields.Boolean(string='Finished', default=False)
    
    # Financial Information
    adm_cost_factor = fields.Float(string='Adm Cost Factor')
    usd_factor = fields.Float(string='USD Factor')
    euro_factor = fields.Float(string='Euro Factor')
    profit = fields.Float(string='Profit %')
    
    # Technical Specifications
    bms = fields.Boolean(string='BMS', default=False)
    selectivity = fields.Boolean(string='Selectivity', default=False)
    current_density = fields.Float(string='Current Density')
    
    # Additional Information
    project_folder = fields.Char(string='Project Folder Path')
    financial_note = fields.Text(string='Financial Note')
    tech_note = fields.Text(string='Technical Note')
    hidden_note = fields.Text(string='Hidden Note')
    
    # Related panels
    panel_ids = fields.One2many('technical.office.project.panel', 'project_id', string='Panels')
    boms_ids = fields.One2many('inventory.boms', 'project_id')
    followup_ids = fields.One2many('technical.office.followup', 'project_id', string='Follow Up')
    # Stats
    panel_count = fields.Integer(string='Number of Panels', compute='_compute_panel_count')
    @api.depends('panel_ids')
    def _compute_panel_count(self):
        for project in self:
            project.panel_count = len(project.panel_ids)
    def action_open_project_panel_form(self):
        return {
            'name': _('Add New Panel'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'technical.office.project.panel',
            'target': 'new',
            'context': {'default_project_id': self.id}
        }
    
    def action_create_project_bom(self):
        """Create or update project-wide BOM"""
        self.ensure_one()
        
        # Check if project BOM already exists
        project_bom = self.env['inventory.boms'].search([
            ('project_id', '=', self.id),
            ('is_project_bom', '=', True)
        ], limit=1)
        
        if not project_bom:
            # Create new project BOM
            project_bom = self.env['inventory.boms'].create({
                'name': f"Project BOM - {self.name}",
                'project_id': self.id,
                'panel_id': False,
                'is_project_bom': True,
            })
        
        # Clear existing lines
        project_bom.bom_line_ids.unlink()
        
        # Get all BOM items from all panels in the project
        all_bom_items = self.env['technical.office.project.bom'].search([
            ('panel_id.project_id', '=', self.id)
        ])
        
        # Group by product and sum quantities
        product_totals = {}
        for bom_item in all_bom_items:
            product_id = bom_item.inventory_product_id.id
            if product_id in product_totals:
                product_totals[product_id] += bom_item.installed_qty
            else:
                product_totals[product_id] = bom_item.installed_qty
        
        # Create BOM lines for project BOM
        for product_id, total_qty in product_totals.items():
            self.env['inventory.boms.line'].create({
                'bom_id': project_bom.id,
                'product_id': product_id,
                'quantity': total_qty,
                'panel_id': False,
            })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project BOM'),
            'res_model': 'inventory.boms',
            'res_id': project_bom.id,
            'view_mode': 'form',
            'target': 'current',
        }

class TechnicalOfficeProjectPanel(models.Model):
    _name = 'technical.office.project.panel'
    _description = 'Project Panels'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('technical.office.project', string='Project', required=True, ondelete='cascade')
    name = fields.Char(string='Panel Name', required=True)
    sn = fields.Char(string='SN')
    
    # Panel dimensions
    enclosure_type = fields.Selection([
        ('A01', 'Chint-lectro EnergiX-M'),
        ('A02', 'Chint-lectro EnergiX-S'),
        ('A03', 'Chint-lectro EnergiX-F'),
        ('A04', 'Lectro')
    ], string='Enclosure Type')
    
    width = fields.Integer(string='Panel Width (mm)')
    height = fields.Integer(string='Panel Height (mm)')
    depth = fields.Integer(string='Panel Depth (mm)')
    sheet_thickness = fields.Selection(string='Panel Sheet Thickness (mm)' , selection=[
        ('A01', '1'),
        ('A02', '1.25'),
        ('A03', '1.5'),
        ('A04', '2.0'),
        ('A05', '2.5'),
        ('A06', '3.0')
    ])
    
    # Panel options
    with_canopy = fields.Boolean(string='With Canopy', default=False)
    with_steel_base = fields.Boolean(string='With Steel Base', default=False)
    used_aluminum_cables = fields.Boolean(string='Used Aluminum Cables', default=False)
    
    # Supply and access options
    supply_from = fields.Char(string='Supply From')
    form_type = fields.Char(string='Form Type')
    painting_color = fields.Char(string='Painting Color')
    
    # Connection points
    incoming = fields.Selection([
        ('A01', 'Top'),
        ('A02', 'Bottom'),
        ('A03', 'Top or Bottom'),
        ('A04', 'Side'),
        ('A05', 'Left Side'),
        ('A06', 'Right Side'),
        ('A07', 'Rear')
    ], string='Incoming')
    
    outgoing = fields.Selection([
        ('A01', 'Top'),
        ('A02', 'Bottom'),
        ('A03', 'Top or Bottom'),
        ('A04', 'Side'),
        ('A05', 'Left Side'),
        ('A06', 'Right Side'),
        ('A07', 'Rear')
    ], string='Outgoing')
    
    access_from = fields.Selection([
        ('A01', 'Front'),
        ('A02', 'Front or Rear'),
        ('A03', 'Front, Rear or Side')
    ], string='Access From')
    
    # Protection ratings
    ip_rating = fields.Char(string='IP Rating')
    ik_rating = fields.Char(string='IK Rating')
    
    # Technical specifications
    cb_spaces = fields.Integer(string='CB Spaces')
    busbar_material = fields.Char(string='Busbar Material')
    busbar_configuration = fields.Char(string='Busbar Configuration')
    busbar_coated = fields.Boolean(string='Busbar Coated', default=False)
    busbar_current_density = fields.Float(string='Busbar Current Density')
    earth_system = fields.Char(string='Earth System')
    
    # Documentation
    enclosure_datasheet = fields.Binary(string='Enclosure Datasheet')
    panel_shop_drawing = fields.Binary(string='Panel Shop Drawing')
    version = fields.Char(string='Version')
    
    # Manufacturing dates
    start_manufacturing_date = fields.Date(string='Starting Manufacturing Date')
    finished_manufacturing_date = fields.Date(string='Finished Manufacturing Date')
    exit_manufacturing_date = fields.Date(string='Exit Manufacturing Date')
    closed = fields.Boolean(string='Closed', default=False)
    
    # Additional information
    note = fields.Text(string='Note')
    panel_unit_price = fields.Float(string='Panel Unit Price')
    parts_note = fields.Text(string='Parts Note')
    panel_cost = fields.Float(string='Panel Cost')
    packing_note = fields.Text(string='Packing Note')
    hidden_note = fields.Text(string='Hidden Note')
    approval_note = fields.Text(string='Approval Note')

    # Cells in this panel
    cell_ids = fields.One2many('technical.office.project.cell', 'panel_id', string='Cells')

    #   BOM in this cell
    bom_ids = fields.One2many('technical.office.project.bom', 'panel_id', string='BOM')
    
     # Panel Phase Tracking
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
    ], string='Current Phase', default='studying', required=True, tracking=True)
    
    phase_start_date = fields.Datetime(string='Phase Start Date', default=fields.Datetime.now)
    phase_history_ids = fields.One2many('technical.office.panel.phase.history', 'panel_id', string='Phase History')
    
    # Phase duration tracking
    studying_duration = fields.Float(string='Studying Duration (Days)', compute='_compute_phase_durations', store=True)
    waiting_approval_duration = fields.Float(string='Waiting Approval Duration (Days)', compute='_compute_phase_durations', store=True)
    manufacture_queue_duration = fields.Float(string='Queue Duration (Days)', compute='_compute_phase_durations', store=True)
    bend_phase_duration = fields.Float(string='Bend Phase Duration (Days)', compute='_compute_phase_durations', store=True)
    painting_duration = fields.Float(string='Painting Duration (Days)', compute='_compute_phase_durations', store=True)
    assembly_duration = fields.Float(string='Assembly Duration (Days)', compute='_compute_phase_durations', store=True)
    copper_formation_duration = fields.Float(string='Copper Formation Duration (Days)', compute='_compute_phase_durations', store=True)
    classic_control_duration = fields.Float(string='Classic Control Duration (Days)', compute='_compute_phase_durations', store=True)
    quality_control_duration = fields.Float(string='Quality Control Duration (Days)', compute='_compute_phase_durations', store=True)
    to_be_exported_duration = fields.Float(string='Export Waiting Duration (Days)', compute='_compute_phase_durations', store=True)
    total_duration = fields.Float(string='Total Duration (Days)', compute='_compute_phase_durations', store=True)
    
    # Progress percentage
    progress_percentage = fields.Float(string='Progress %', compute='_compute_progress_percentage', store=True)
    
    def action_open_project_panel_bom_form(self):
        return {
            'name': _('Add Items to BOM'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'technical.office.project.bom',
            'target': 'new',
            'context': {'default_panel_id': self.id}
        }

    #make sure quntity in BOM is less than or equal to the quantity in the inventory stock
    @api.constrains('inventory_line_ids')
    def _check_inventory_quantity(self):
        stock_item = self.env['inventory.stock'].search([
                ('product_id', '=', self.inventory_line_ids.product_id.id)
            ], limit=1)
        for panel in self:
            for line in panel.inventory_line_ids:
                if line.quantity > stock_item.quantity:
                    #return a warning message 
                    return {
                        'warning': {
                            'title': _('Warning!'),
                            'message': _('The quantity in BOM is greater than the quantity in stock.'),
                        }
                    }

    @api.depends('phase_history_ids', 'phase_start_date', 'phase')
    def _compute_phase_durations(self):
        for panel in self:
            # Initialize all durations to 0
            panel.studying_duration = 0
            panel.waiting_approval_duration = 0
            panel.manufacture_queue_duration = 0
            panel.bend_phase_duration = 0
            panel.painting_duration = 0
            panel.assembly_duration = 0
            panel.copper_formation_duration = 0
            panel.classic_control_duration = 0
            panel.quality_control_duration = 0
            panel.to_be_exported_duration = 0
            panel.total_duration = 0
            
            # Calculate durations from history
            for history in panel.phase_history_ids:
                if history.end_date:
                    duration = (history.end_date - history.start_date).total_seconds() / 86400  # Convert to days
                    if history.phase == 'studying':
                        panel.studying_duration = duration
                    elif history.phase == 'waiting_approval':
                        panel.waiting_approval_duration = duration
                    elif history.phase == 'manufacture_queue':
                        panel.manufacture_queue_duration = duration
                    elif history.phase == 'bend_phase':
                        panel.bend_phase_duration = duration
                    elif history.phase == 'painting':
                        panel.painting_duration = duration
                    elif history.phase == 'assembly':
                        panel.assembly_duration = duration
                    elif history.phase == 'copper_formation':
                        panel.copper_formation_duration = duration
                    elif history.phase == 'classic_control':
                        panel.classic_control_duration = duration
                    elif history.phase == 'quality_control':
                        panel.quality_control_duration = duration
                    elif history.phase == 'to_be_exported':
                        panel.to_be_exported_duration = duration
            
            # Calculate total duration
            panel.total_duration = (
                panel.studying_duration + panel.waiting_approval_duration +
                panel.manufacture_queue_duration + panel.bend_phase_duration +
                panel.painting_duration + panel.assembly_duration +
                panel.copper_formation_duration + panel.classic_control_duration +
                panel.quality_control_duration + panel.to_be_exported_duration
            )
    
    @api.depends('phase')
    def _compute_progress_percentage(self):
        phase_weights = {
            'studying': 10,
            'waiting_approval': 20,
            'manufacture_queue': 25,
            'bend_phase': 35,
            'painting': 45,
            'assembly': 60,
            'copper_formation': 75,
            'classic_control': 85,
            'quality_control': 95,
            'to_be_exported': 98,
            'completed': 100
        }
        
        for panel in self:
            panel.progress_percentage = phase_weights.get(panel.phase, 0)
    
    def write(self, vals):
        # Track phase changes
        if 'phase' in vals:
            for panel in self:
                old_phase = panel.phase
                new_phase = vals['phase']
                
                if old_phase != new_phase:
                    # End current phase history
                    current_history = self.env['technical.office.panel.phase.history'].search([
                        ('panel_id', '=', panel.id),
                        ('phase', '=', old_phase),
                        ('end_date', '=', False)
                    ], limit=1)
                    
                    if current_history:
                        current_history.write({'end_date': fields.Datetime.now()})
                    
                    # Create new phase history
                    self.env['technical.office.panel.phase.history'].create({
                        'panel_id': panel.id,
                        'phase': new_phase,
                        'start_date': fields.Datetime.now(),
                        'user_id': self.env.user.id
                    })
        
        result = super(TechnicalOfficeProjectPanel, self).write(vals)
        return result
    
    @api.model
    def create(self, vals):
        # Create initial phase history
        panel = super(TechnicalOfficeProjectPanel, self).create(vals)
        
        self.env['technical.office.panel.phase.history'].create({
            'panel_id': panel.id,
            'phase': panel.phase,
            'start_date': fields.Datetime.now(),
            'user_id': self.env.user.id
        })
        
        return panel
    
    def action_advance_phase(self):
        """Advance panel to next phase"""
        phase_sequence = [
            'studying', 'waiting_approval', 'manufacture_queue', 'bend_phase',
            'painting', 'assembly', 'copper_formation', 'classic_control',
            'quality_control', 'to_be_exported', 'completed'
        ]
        
        current_index = phase_sequence.index(self.phase)
        if current_index < len(phase_sequence) - 1:
            next_phase = phase_sequence[current_index + 1]
            self.write({'phase': next_phase})
    
    def action_previous_phase(self):
        """Move panel to previous phase"""
        phase_sequence = [
            'studying', 'waiting_approval', 'manufacture_queue', 'bend_phase',
            'painting', 'assembly', 'copper_formation', 'classic_control',
            'quality_control', 'to_be_exported', 'completed'
        ]
        
        current_index = phase_sequence.index(self.phase)
        if current_index > 0:
            previous_phase = phase_sequence[current_index - 1]
            self.write({'phase': previous_phase})

class technicalOfficeProjectCell(models.Model):
    _name = 'technical.office.project.cell'
    _description = 'Panel Cells'
    
    panel_id = fields.Many2one('technical.office.project.panel', string='Panel', 
                               required=True, ondelete='cascade',
                               domain="[('can_add_cells', '=', True)]")
    name = fields.Char(string='Cell Name', required=True)
    sn = fields.Char(string='SN')
    section = fields.Char(string='Section')
    
    # Cell dimensions
    width = fields.Integer(string='Cell Width (mm)')
    height = fields.Integer(string='Cell Height (mm)')
    depth = fields.Integer(string='Cell Depth (mm)')
    
    # Cell options
    two_part_door = fields.Boolean(string='Two Part Door', default=False)
    no_of_sides = fields.Integer(string='Number of Sides')
    
    # Connection points
    incoming_from = fields.Selection([
        ('A01', 'Top'),
        ('A02', 'Bottom'),
        ('A03', 'Top or Bottom'),
        ('A04', 'Side'),
        ('A05', 'Left Side'),
        ('A06', 'Right Side'),
        ('A07', 'Rear')
    ], string='Incoming From')
    
    outgoing_from = fields.Selection([
        ('A01', 'Top'),
        ('A02', 'Bottom'),
        ('A03', 'Top or Bottom'),
        ('A04', 'Side'),
        ('A05', 'Left Side'),
        ('A06', 'Right Side'),
        ('A07', 'Rear')
    ], string='Outgoing From')
    
    access_from = fields.Selection([
        ('A01', 'Front'),
        ('A02', 'Front or Rear'),
        ('A03', 'Front, Rear or Side')
    ], string='Access From')
    
    note = fields.Text(string='Cell Note')
    
class technicalOfficeProjectBOM(models.Model):
    _name = 'technical.office.project.bom'
    _description = 'Panel BOM'
    
    inventory_product_id = fields.Many2one('inventory.product', string='Product', required=True)
    product_id = fields.Char(related='inventory_product_id.name', string='Product', required=True)
    inventory_product_qty = fields.Integer(related='inventory_product_id.current_stock_qty', string='Current Stock Quantity')
    panel_id = fields.Many2one('technical.office.project.panel', string='Panel')
    installed_qty = fields.Integer(string='Installed Quantity')    
    item_category = fields.Selection([
        ('A01', 'CB'),
        ('A02', 'Control'),
        ('A03', 'Bars'),
        ('A04', 'Enclosure')
    ], string='Item Category')
    
    note = fields.Text(string='Note')
    
    @api.model
    def create(self, vals):
        record = super(technicalOfficeProjectBOM, self).create(vals)
        
        # Get the project from the panel
        project = record.panel_id.project_id
        
        # Check if an inventory BOM already exists for this project
        inventory_bom = self.env['inventory.boms'].search([
            ('project_id', '=', project.id),
            ('is_project_bom', '=', False)
        ], limit=1)
        
        if not inventory_bom:
            # Create new inventory BOM record for the panel
            inventory_bom = self.env['inventory.boms'].create({
                'name': f"BOM for {record.panel_id.project_id.name} ",
                'project_id': project.id,
                'panel_id': record.panel_id.id,
                'is_project_bom': False,
            })
        
        # Create the BOM line for the panel
        self.env['inventory.boms.line'].create({
            'bom_id': inventory_bom.id,
            'product_id': record.inventory_product_id.id,
            'quantity': record.installed_qty,
            'panel_id': record.panel_id.id,
        })
        
        # Auto-update project BOM
        self._update_project_bom(project)
        
        return record

    def _update_project_bom(self, project):
        """Update or create project-wide BOM"""
        # Check if project BOM exists
        project_bom = self.env['inventory.boms'].search([
            ('project_id', '=', project.id),
            ('is_project_bom', '=', True)
        ], limit=1)
        
        if not project_bom:
            # Create new project BOM
            project_bom = self.env['inventory.boms'].create({
                'name': f"Project BOM - {project.name}",
                'project_id': project.id,
                'panel_id': False,
                'is_project_bom': True,
            })
        
        # Clear existing lines
        project_bom.bom_line_ids.unlink()
        
        # Get all BOM items from all panels in the project
        all_bom_items = self.search([
            ('panel_id.project_id', '=', project.id)
        ])
        
        # Group by product and sum quantities
        product_totals = {}
        for bom_item in all_bom_items:
            product_id = bom_item.inventory_product_id.id
            if product_id in product_totals:
                product_totals[product_id] += bom_item.installed_qty
            else:
                product_totals[product_id] = bom_item.installed_qty
        
        # Create BOM lines for project BOM
        for product_id, total_qty in product_totals.items():
            self.env['inventory.boms.line'].create({
                'bom_id': project_bom.id,
                'product_id': product_id,
                'quantity': total_qty,
                'panel_id': False,
            })

    @api.depends('installed_qty' ,)
    def _compute_total_weight(self):
        for bom in self:
                bom.product_id = bom.product_id - bom.installed_qty
