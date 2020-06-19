import odoo
from odoo import api, fields, models
import time
import os
import base64
import logging
import math

_logger = logging.getLogger(__name__)


class BackupConfiguration(models.Model):
    _name = "rg.backup.configuration"
    _description = 'Configuration Rules For Backups'

    name = fields.Char(string='Name', required=True)
    backup_type = fields.Selection([('sql', 'Dump'), ('zip', 'Zip')], string="Backup Type", required=True, default="zips")
    backup_ids = fields.One2many("rg.backup", "configuration_id", string="Backups")
    backup_folder = fields.Char(string="Backup Folder Path", required=True)

    def backup_database(self):
        current_time = time.strftime('%Y_%m_%d_%H_%M_%S')
        name = 'Backup [%s_%s]' % (self.env.cr.dbname, current_time)
        bkp_file = '%s_%s.%s' % (self.env.cr.dbname, current_time, self.backup_type)
        file_path = os.path.join(self.backup_folder, bkp_file)

        backup_env = self.env["rg.backup"]

        with open(file_path, "wb") as fp:
            odoo.service.db.dump_db(self.env.cr.dbname, fp, self.backup_type)

        with open(file_path, "rb") as rf:
            readable_size = backup_env._convert_size(len(rf.read()))

        rec = backup_env.sudo().create({"name": name, "configuration_id": self.id, "file_path": file_path, "file_name": bkp_file, "size": readable_size})
        return rec

    def download_now(self):
        rec = self.backup_database()
        return rec.download(unlink=True)


class Backup(models.Model):
    _name = 'rg.backup'
    _description = 'Actual Backup'

    name = fields.Char(string='Name', required=True)
    configuration_id = fields.Many2one('rg.backup.configuration', string="Related Configuration", required=True)
    file_name = fields.Char(string="Backup File Name")
    file_path = fields.Char(string="Backup File Path", required=True)
    size = fields.Char(string="Size")

    def download(self, unlink=False):
        return {"type": "ir.actions.act_url", "url": "/backups/download?rec_id=%s&unlink=%s" % (self.id, unlink), "target": "new"}

    def _get_encoded(self):
        with open(self.file_path, 'rb') as backup_file:
            f = backup_file.read()
        return base64.b64encode(f)

    @api.model
    def _convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])


    @api.multi
    def unlink(self):
        for record in self:
            try:
                os.remove(record.file_path)
            except Exception:
                _logger.exception("An error occured while deleting a backup file.")
        super(Backup, self).unlink()
