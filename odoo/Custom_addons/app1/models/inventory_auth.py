from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import random
import string


class InventoryAuth(models.Model):
    _name = 'inventory.auth'
    _description = 'Inventory Authorization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Authorization Number', required=True, 
                       default=lambda self: self.env['ir.sequence'].next_by_code('inventory.auth'))
    type = fields.Selection(string='Authorization', selection=[
        ('in', 'Authorization to Enter'),
        ('out', 'Authorization to Issue')
    ], required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By')
    canceled_by = fields.Many2one('res.users', string='Canceled By')
    supplier_company = fields.Char( string='Supplier Company')
    supplier_name = fields.Char( string='Supplier Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft')
    line_ids = fields.One2many('inventory.auth.line', 'auth_id', string='Products', required=True)
    notes = fields.Text(string='Notes')
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id
        })
    
    def action_done(self):
        # Only process "in" authorizations
        self._create_stock_entries()
        self.write({'state': 'done'})
    
    def action_cancel(self):
        
        self.write({
            'state': 'canceled',
            'canceled_by': self.env.user.id
        })
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    def action_open_product_form(self):
        """Open a form to add a new product line"""
        self.ensure_one()
        
        # Instead of creating the record first, pass the default values in the context
        return {
            'name': _('Add New Product'),
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.auth.line',
            'view_mode': 'form',
            'view_id': self.env.ref('app1.view_inventory_auth_line_form').id,  
            'target': 'new',
            'context': {
                'default_auth_id': self.id,
            },
        }
    
    def _create_stock_entries(self):
        """Create or update inventory stock entries based on authorization lines"""
        product_obj = self.env['inventory.product']
        
        for line in self.line_ids:
            # Check if product already exists in stock with this product
            stock_item = product_obj.search([
                ('name', '=', line.product_id.name)
            ], limit=1)
            
            if stock_item:
                # Product exists in stock, maintain same item code
                if not line.item_code:
                    line.write({'item_code': stock_item.item_code})
                
                if self.type == 'in':
                    # Update existing stock item
                    stock_item.write({
                        'current_stock_qty': stock_item.current_stock_qty + line.quantity
                    })
                elif self.type == 'out':
                    if stock_item.current_stock_qty < line.quantity:
                        raise ValidationError(_('Insufficient stock for product %s') % (line.product_id.name))
                    else:
                        stock_item.write({
                            'current_stock_qty': stock_item.current_stock_qty - line.quantity
                        })
            else:
                # Product doesn't exist in stock yet
                if not line.item_code:
                    # Generate new item code if needed
                    line._generate_item_code()
                
                # Create new stock item
                product_obj.create({
                    'name': line.product_id.id,
                    'sn': line.item_code,
                    'current_stock_qty': line.quantity,
                    'location': line.location_id,
                    'price': line.price
                })

class InventoryAuthLine(models.Model):
    _name = 'inventory.auth.line'
    _description = 'Inventory Authorization Line'
    
    auth_id = fields.Many2one('inventory.auth', string='Authorization', ondelete='cascade')
    # Changed to Many2one field to enable dropdown/combobox suggestion feature
    bom_id = fields.Many2one('technical.office.project.panel', string='BOM', ondelete='cascade')

    # Added domain to search existing products
    product_id = fields.Many2one('inventory.product', string='Product', required=True)
    item_code = fields.Char(string='Item Code', size=5, readonly=True)
    uom_id = fields.Selection(string='Unit of Measure', selection=[
        ('kg', 'Kilograms'), 
        ('gm', 'Gram'), 
        ('m', 'Meters'), 
        ('cm', 'Centimeters'), 
        ('mm', 'Millimeters'),  
        ('pcs', 'Pieces')
    ], required=True, default='pcs')
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price = fields.Float(string='Unit Price')
    location_id = fields.Integer(string='Stand number')
    notes = fields.Text(string='Notes')
    

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """When product changes, find existing item code if available"""
        if self.product_id:
            # Search for existing product in inventory stock
            stock_item = self.env['inventory.product'].search([
                ('name', '=', self.product_id.name)
            ], limit=1)
            
            if stock_item:
                # If product exists in stock, use its item code
                self.item_code = stock_item.item_code
                # Also set other fields based on existing product
                self.price = stock_item.price
            else:
                # Product doesn't exist in stock yet, generate new code
                self._generate_item_code()
                # Set default values from product
                if self.product_id.default_uom_id:
                    self.uom_id = self.product_id.default_uom_id
                if self.product_id.price:
                    self.price = self.product_id.price
                if self.product_id.location:
                    self.location_id = self.product_id.location
    
    def _generate_item_code(self):
        """Generate a unique item code for a new product"""
        while True:
            new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            # Check if this code already exists
            if not self.search([('item_code', '=', new_code)]) and not self.env['inventory.product'].search([('item_code', '=', new_code)]):
                self.item_code = new_code
                break
    
    def save_product_line(self):
        """Save the product line and return to parent form"""
        self.ensure_one()
        # Make sure the item code is generated if not already set
        if not self.item_code and self.product_id:
            self._generate_item_code()
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_edit_product_form(self):
        """Open the form to edit this product line"""
        self.ensure_one()
        return {
            'name': _('Edit Product'),
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.auth.line',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('app1.view_inventory_auth_line_form').id,  # Replace 'app1' with your actual module name
            'target': 'new',
        }

class InventoryProduct(models.Model):
    _name = 'inventory.product'
    _description = 'Inventory Products'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Product Name', required=True)
    default_uom_id = fields.Selection(string='Default Unit of Measure', selection=[
        ('kg', 'Kilograms'), 
        ('gm', 'Gram'), 
        ('m', 'Meters'), 
        ('cm', 'Centimeters'), 
        ('mm', 'Millimeters'),  
        ('pcs', 'Pieces')
    ], default='pcs')
    item_code = fields.Char(string='Item Code', size=5, readonly=True)
    sn = fields.Char(string='Serial Number', size=50, required=True)  
    brand = fields.Char(string='Brand', size=50)
    category = fields.Char(string='Category', size=50)
    keyword = fields.Text(string='Keyword')  
    catalog_name = fields.Text(string='Catalog Name')
    order_code = fields.Char(string='Order Code', size=50)
    current_stock_qty = fields.Integer(string='Current Stock QTY')  
    currency = fields.Selection(string='Currency', selection=[
        ('EGP', 'Egyptian Pound'), 
        ('USD', 'US Dollar') 
    ], default='EGP', required=True)  
    
    location = fields.Char(string='Location', size=100)
    minimum_stock = fields.Float(string='Minimum Stock')
    datasheet_url = fields.Char(string='Datasheet URL')  
    item_weight_kg = fields.Float(string='Item Weight (KG)')
    item_volume = fields.Char(string='Item Volume', size=50)
    item_dimensions = fields.Char(string='Item Dimensions', size=100)
    installation_time = fields.Float(string='Installation Time')
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Product name must be unique!')
    ]
    price = fields.Float(string='Unit Price', required=True)
    total_price = fields.Float(string='Total Price' , compute='_compute_total_price')
    @api.depends('price' , 'current_stock_qty')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.current_stock_qty * record.price

    @api.onchange('current_stock_qty' , 'minimum_stock')
    def alertMinStock(self):
        if self.current_stock_qty <= self.minimum_stock:
            return{
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Minimum Stock Reached.')
                }
            }

    @api.model
    def write(self, vals):
        """Override write to check BOM deduction status when stock is updated"""
        result = super(InventoryProduct, self).write(vals)
        
        if 'current_stock_qty' in vals:
            # Find all BOMs that use this product and check replenishment
            bom_lines = self.env['inventory.boms.line'].search([('product_id', 'in', self.ids)])
            for line in bom_lines:
                if line.bom_id:
                    line.bom_id._check_stock_replenishment()
        
        return result

class InventoryBOMs(models.Model):
    _name = 'inventory.boms'
    _description = 'Inventory BOMs'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='BOM Name', required=True)
    project_id = fields.Many2one('technical.office.project', string='Project name', required=True)
    numbers_of_panels = fields.Integer(related='project_id.panel_count', string='Number of panels', readonly=True)
    panel_id = fields.Many2one('technical.office.project.panel', string='Panel', 
                              domain="[('project_id', '=', project_id)]")
    user = fields.Many2one('res.users', default=lambda self: self.env.user)
    date = fields.Date(string='Date', default=fields.Date.today)
    has_bom = fields.Boolean(string='Has BOM', compute='_compute_has_bom', store=True)
    deducted = fields.Boolean(string='Already Deducted', default=False)
    bom_line_ids = fields.One2many('inventory.boms.line', 'bom_id', string='BOM Lines')
    notes = fields.Text(string='Notes')
    is_project_bom = fields.Boolean(string='Project BOM', default=False, help="Indicates this is a project-wide BOM")
    
    @api.depends('panel_id')
    def _compute_has_bom(self):
        for record in self:
            if record.panel_id:
                record.has_bom = bool(self.env['technical.office.project.bom'].search_count([
                    ('panel_id', '=', record.panel_id.id)
                ]))
            else:
                record.has_bom = False
    
    @api.onchange('project_id')
    def _onchange_project_id(self):
        """When project changes, reset panel selection"""
        self.panel_id = False
        self.bom_line_ids = [(5, 0, 0)]  # Clear all lines
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure proper BOM line synchronization"""
        records = super(InventoryBOMs, self).create(vals_list)
        for record in records:
            record._sync_bom_lines()
        return records

    def write(self, vals):
        """Override write to ensure BOM lines are refreshed when panel changes"""
        result = super(InventoryBOMs, self).write(vals)
        
        # If panel_id is changed, refresh the BOM lines
        if 'panel_id' in vals:
            for record in self:
                record._sync_bom_lines()
        
        return result

    def _sync_bom_lines(self):
        """Synchronize BOM lines with the selected panel's BOM items"""
        self.ensure_one()
        
        if not self.panel_id:
            return
            
        # Clear existing lines
        self.bom_line_ids.unlink()
        
        # Get fresh BOM items from the selected panel
        bom_items = self.env['technical.office.project.bom'].search([
            ('panel_id', '=', self.panel_id.id)
        ])
        
        # Create new BOM lines
        line_vals = []
        for item in bom_items:
            line_vals.append((0, 0, {
                'product_id': item.inventory_product_id.id,
                'quantity': item.installed_qty,
                'panel_id': self.panel_id.id,
                'deducted_qty': 0.0,  # Reset deducted quantity
            }))
        
        if line_vals:
            self.bom_line_ids = line_vals


    @api.onchange('panel_id')
    def onchange_panel_id(self):
        """Enhanced onchange to ensure fresh data"""
        result = {'domain': {}}
        
        if self.panel_id:
            # Force refresh of BOM items from database
            self.env['technical.office.project.bom']._invalidate_cache()
            
            # Get fresh BOM items
            bom_items = self.env['technical.office.project.bom'].search([
                ('panel_id', '=', self.panel_id.id)
            ])
            
            # Clear existing lines
            self.bom_line_ids = [(5, 0, 0)]
            
            # Create new lines with fresh data
            line_vals = []
            for item in bom_items:
                line_vals.append((0, 0, {
                    'product_id': item.inventory_product_id.id,
                    'quantity': item.installed_qty,
                    'panel_id': self.panel_id.id,
                    'deducted_qty': 0.0,
                }))
            
            if line_vals:
                self.bom_line_ids = line_vals
        else:
            # Clear lines if no panel selected
            self.bom_line_ids = [(5, 0, 0)]
        
        return result

    def action_create_project_bom(self):
        """Create or update project-wide BOM that combines all panels"""
        self.ensure_one()
        
        if not self.project_id:
            raise ValidationError(_('Project is required to create project BOM.'))
        
        # Check if project BOM already exists
        project_bom = self.search([
            ('project_id', '=', self.project_id.id),
            ('is_project_bom', '=', True)
        ], limit=1)
        
        if not project_bom:
            # Create new project BOM
            project_bom = self.create({
                'name': f"Project BOM - {self.project_id.name}",
                'project_id': self.project_id.id,
                'panel_id': False,  # No specific panel for project BOM
                'is_project_bom': True,
            })
        
        # Clear existing lines
        project_bom.bom_line_ids.unlink()
        
        # Get all BOM items from all panels in the project
        all_bom_items = self.env['technical.office.project.bom'].search([
            ('panel_id.project_id', '=', self.project_id.id)
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
                'panel_id': False,  # No specific panel for project BOM
            })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project BOM'),
            'res_model': 'inventory.boms',
            'res_id': project_bom.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _check_stock_replenishment(self):
        """Check if stock has been replenished and update deducted status"""
        if self.deducted:
            # Check if any line now has remaining quantity due to stock replenishment
            if self.bom_line_ids.filtered(lambda l: l.remaining_qty > 0):
                self.write({'deducted': False})    

    def action_deduct_inventory(self):
        """Deduct remaining BOM quantities from inventory stock"""
        self.ensure_one()
        
        # Get lines that still have quantities to deduct
        lines_to_deduct = self.bom_line_ids.filtered(lambda l: l.remaining_qty > 0)
        
        if not lines_to_deduct:
            raise ValidationError(_('No remaining quantities to deduct from inventory.'))
        
        warnings = []
        
        for line in lines_to_deduct:
            product = line.product_id
            current_stock = product.current_stock_qty
            required_qty = line.remaining_qty
            
            if current_stock >= required_qty:
                # Sufficient stock - deduct full remaining quantity
                product.write({
                    'current_stock_qty': current_stock - required_qty
                })
                line.write({
                    'deducted_qty': line.deducted_qty + required_qty
                })
            elif current_stock > 0:
                # Partial stock - deduct what's available
                shortage = required_qty - current_stock
                product.write({
                    'current_stock_qty': 0
                })
                line.write({
                    'deducted_qty': line.deducted_qty + current_stock
                })
                warnings.append(f"{product.name}: {shortage} units still needed")
            else:
                # No stock available
                warnings.append(f"{product.name}: {required_qty} units needed (no stock available)")
        
        # Check if all quantities are now deducted
        if not self.bom_line_ids.filtered(lambda l: l.remaining_qty > 0):
            self.write({'deducted': True})
        
        # Display warnings if any
        if warnings:
            warning_message = "Inventory deduction completed with shortages:\n\n" + "\n".join(warnings)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Inventory Deduction Warning'),
                    'message': warning_message,
                    'type': 'warning',
                    'sticky': True,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Inventory quantities deducted successfully.'),
                    'type': 'success',
                }
            }

class InventoryBOMsLine(models.Model):
    _name = 'inventory.boms.line'
    _description = 'Inventory BOMs Line'
    
    bom_id = fields.Many2one('inventory.boms', string='BOM', ondelete='cascade')
    product_id = fields.Many2one('inventory.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    panel_id = fields.Many2one('technical.office.project.panel', string='Panel')
    price = fields.Float(related='product_id.price', string='Unit Price', readonly=True)
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    deducted_qty = fields.Float(string='Deducted Quantity', default=0.0)
    remaining_qty = fields.Float(string='Remaining to Deduct', compute='_compute_remaining_qty', store=True)
    
    @api.depends('quantity', 'price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.price

    @api.depends('quantity', 'deducted_qty')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.quantity - line.deducted_qty
