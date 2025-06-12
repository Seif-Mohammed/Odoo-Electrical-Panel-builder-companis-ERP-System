from odoo import models, fields, api, _
from odoo.exceptions import UserError
import os
import base64
import subprocess
import platform


class ManufacturingDrawingDownload(models.Model):
    _name = 'manufacturing.drawing.download'
    _description = 'Manufacturing Drawing Download'

    project_id = fields.Many2one(
        'technical.office.project', 
        string='Project', 
        required=True,
        help="Select the project to view its panels"
    )
    
    panel_id = fields.Many2one(
        'technical.office.project.panel', 
        string='Panel', 
        required=True,
        domain="[('project_id', '=', project_id)]",
        help="Select the panel to download its drawing"
    )
    
    # Display panel information
    panel_info = fields.Text(
        string='Panel Information',
        compute='_compute_panel_info',
        readonly=True
    )
    
    drawing_file_name = fields.Char(
        string='Drawing File Name',
        compute='_compute_drawing_file_name',
        readonly=True
    )
    
    file_exists = fields.Boolean(
        string='File Exists',
        compute='_compute_file_exists',
        readonly=True
    )
    
    @api.depends('panel_id')
    def _compute_panel_info(self):
        for record in self:
            if record.panel_id:
                panel = record.panel_id
                enclosure_types = {
                    'A01': 'Chint-lectro EnergiX-M',
                    'A02': 'Chint-lectro EnergiX-S', 
                    'A03': 'Chint-lectro EnergiX-F',
                    'A04': 'Lectro'
                }
                
                enclosure_name = enclosure_types.get(panel.enclosure_type, 'Unknown')
                
                record.panel_info = f"""
                    Panel: {panel.name}
                    Enclosure Type: {enclosure_name} ({panel.enclosure_type})
                    Dimensions: {panel.width}mm x {panel.height}mm x {panel.depth}mm
                    Phase: {dict(panel._fields['phase'].selection).get(panel.phase, panel.phase)}
                    Current Phase: {panel.phase}"""
            else:
                record.panel_info = ""
    
    @api.depends('panel_id')
    def _compute_drawing_file_name(self):
        for record in self:
            if record.panel_id:
                panel = record.panel_id
                # Create file name based on naming convention:
                # {enclosure_type}_{width}x{height}x{depth}.dwg
                record.drawing_file_name = f"{panel.enclosure_type}_{panel.width}x{panel.height}x{panel.depth}.dwg"
            else:
                record.drawing_file_name = ""
    
    @api.depends('drawing_file_name')
    def _compute_file_exists(self):
        for record in self:
            if record.drawing_file_name:
                # Get the drawing directory from system parameter
                drawing_dir = self.env['ir.config_parameter'].sudo().get_param(
                    'manufacturing.drawing_directory', 
                    '/home/seif/Desktop/odoo18/odoo/Custom_addons/app1/drawings'
                )
                file_path = os.path.join(drawing_dir, record.drawing_file_name)
                record.file_exists = os.path.exists(file_path)
            else:
                record.file_exists = False
    
    def action_download_drawing(self):
        """Download the drawing file for the selected panel"""
        self.ensure_one()
        
        if not self.panel_id:
            raise UserError(_("Please select a panel first."))
        
        if not self.file_exists:
            raise UserError(_(
                "Drawing file '%s' not found in the drawings directory. "
                "Please contact the administrator to add the missing drawing file."
            ) % self.drawing_file_name)
        
        # Get the drawing directory from system parameter
        drawing_dir = self.env['ir.config_parameter'].sudo().get_param(
            'manufacturing.drawing_directory', 
            '/home/seif/Desktop/odoo18/odoo/Custom_addons/app1/drawings'
        )
        
        file_path = os.path.join(drawing_dir, self.drawing_file_name)
        
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_base64 = base64.b64encode(file_data)
            
            # Create attachment for download
            attachment = self.env['ir.attachment'].create({
                'name': self.drawing_file_name,
                'type': 'binary',
                'datas': file_base64,
                'res_model': 'technical.office.project.panel',
                'res_id': self.panel_id.id,
                'mimetype': 'application/acad'
            })
            
            # Log the download activity
            self.panel_id.message_post(
                body=_("Drawing file '%s' downloaded by %s") % (
                    self.drawing_file_name, 
                    self.env.user.name
                ),
                message_type='notification'
            )
            
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
            
        except IOError as e:
            raise UserError(_("Error reading drawing file: %s") % str(e))
        except Exception as e:
            raise UserError(_("Unexpected error occurred: %s") % str(e))
    
    def action_view_panel_details(self):
        """Open the selected panel in form view"""
        if not self.panel_id:
            raise UserError(_("Please select a panel first."))
        
        return {
            'name': _('Panel Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'technical.office.project.panel',
            'res_id': self.panel_id.id,
            'target': 'current',
        }
    
    def action_open_busbar_calculator(self):
        """Open the Busbar Calculator HTML application"""
        # Get the calculator path from system parameter
        calculator_path = self.env['ir.config_parameter'].sudo().get_param(
            'manufacturing.busbar_calculator_path',
            '/app1/static/src/http/copper_busbar_calculator.html'
        )   
        return {
            'type': 'ir.actions.act_url',
            'url': calculator_path,
            'target': 'new',
        }


class ManufacturingDrawingConfig(models.Model):
    _name = 'manufacturing.drawing.config'
    _inherit = 'res.config.settings'
    _description = 'Manufacturing Drawing Configuration'
    
    drawing_directory = fields.Char(
        string="Drawing Files Directory",
        config_parameter='manufacturing.drawing_directory',
        default='/home/seif/Desktop/odoo18/odoo/Custom_addons/app1/drawings',
        help="Directory path where .dwg drawing files are stored"
    )
    
    # NEW: Busbar Calculator Path Configuration
    busbar_calculator_path = fields.Char(
        string="Busbar Calculator Path",
        config_parameter='manufacturing.busbar_calculator_path',
        default='/home/user/copper_busbar_calculator.html',
        help="Full path to the Copper Busbar Calculator HTML file"
    )
    
    def action_test_directory(self):
        """Test if the drawing directory exists and is accessible"""
        if not self.drawing_directory:
            raise UserError(_("Please specify a drawing directory first."))
        
        if not os.path.exists(self.drawing_directory):
            raise UserError(_("Directory '%s' does not exist.") % self.drawing_directory)
        
        if not os.access(self.drawing_directory, os.R_OK):
            raise UserError(_("Directory '%s' is not readable.") % self.drawing_directory)
        
        # Count .dwg files in directory
        dwg_files = [f for f in os.listdir(self.drawing_directory) if f.lower().endswith('.dwg')]
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Directory Test Successful'),
                'message': _('Directory is accessible. Found %d .dwg files.') % len(dwg_files),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_list_drawings(self):
        """List all available drawing files"""
        if not self.drawing_directory or not os.path.exists(self.drawing_directory):
            raise UserError(_("Drawing directory is not configured or does not exist."))
        
        try:
            dwg_files = [f for f in os.listdir(self.drawing_directory) if f.lower().endswith('.dwg')]
            dwg_files.sort()
            
            if not dwg_files:
                message = _("No .dwg files found in the directory.")
            else:
                message = _("Found %d drawing files:\n\n%s") % (
                    len(dwg_files), 
                    '\n'.join(dwg_files)
                )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Available Drawing Files'),
                    'message': message,
                    'type': 'info',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            raise UserError(_("Error accessing directory: %s") % str(e))
    
    # NEW: Test Busbar Calculator Path
    def action_test_calculator_path(self):
        """Test if the busbar calculator file exists"""
        if not self.busbar_calculator_path:
            raise UserError(_("Please specify the busbar calculator path first."))
        
        if not os.path.exists(self.busbar_calculator_path):
            raise UserError(_("Busbar Calculator file '%s' does not exist.") % self.busbar_calculator_path)
        
        if not os.access(self.busbar_calculator_path, os.R_OK):
            raise UserError(_("Busbar Calculator file '%s' is not readable.") % self.busbar_calculator_path)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Calculator Path Test Successful'),
                'message': _('Busbar Calculator file is accessible and ready to use.'),
                'type': 'success',
                'sticky': False,
            }
        }

