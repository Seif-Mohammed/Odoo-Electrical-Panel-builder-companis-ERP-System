from odoo.tests.common import TransactionCase


class TestTechnicalOffice(TransactionCase):
    def setUp(self ,*args, **kwargs):
        super().setUp(*args, **kwargs)
        self.techTest1 = self.env['technical.office.project'].create({
            'name': 'Test Technical Office proj1',
            'project_sn': '111',
        })
