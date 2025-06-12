from odoo import http

class ManufacturingEntryController(http.Controller):
    @http.route( '/manufacturing/entry', methods=['GET'], type='http', auth="none", csrf=False)
    def manufacturing_entry(self):
        # Logic for handling manufacturing entry
        print("Manufacturing entry logic executed")