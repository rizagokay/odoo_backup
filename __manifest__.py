# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Backup Database',
    'version': '12.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Adds backup function without downloading from web client',
    'author': "Rıza Gökay Kıvırcıoğlu",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        ],
    'installable': True,
}
