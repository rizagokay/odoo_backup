
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import base64
import mimetypes


import logging

_logger = logging.getLogger(__name__)


class BackupDownloadController(http.Controller):
    @http.route(["/backups/download"], type="http", auth="user")
    def download_(self, rec_id, unlink=False, **kwargs):
        rec = request.env["rg.backup"].search([('id', '=', rec_id)])
        if rec:
            data = base64.b64decode(rec._get_encoded())
            file_name = rec.file_name
            if unlink:
                rec.unlink()
            return http.request.make_response(data, headers=[
                ('Content-Length', len(data)),
                ('Content-Type', mimetypes.guess_type(file_name)[0] or 'application/octet-stream'), 
                ('Content-Disposition', content_disposition(file_name))])
