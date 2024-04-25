# TODO: add license to all files.
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    industry_id = fields.Many2one(
        string="Main Industry",
        comodel_name="res.partner.industry",
    )

    secondary_industry_ids = fields.Many2many(
        comodel_name="res.partner.industry",
        string="Secondary Industries",
        domain="[('id', '!=', industry_id)]",
    )

    def _prepare_customer_values(self, name, is_company, parent_id=False):
        """Propagate NACE activity to created partner."""
        result = super()._prepare_customer_values(name, is_company, parent_id)
        if self.industry_id:
            result["industry_id"] = self.industry_id.id
        if self.secondary_industry_ids:
            result["secondary_industry_ids"] = [
                (4, id_) for id_ in self.secondary_industry_ids.ids
            ]
        return result
