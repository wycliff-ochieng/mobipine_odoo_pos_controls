# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _ensure_pos_customer_permission(self):
        """Check if the current user (via linked employee) can manage customers from POS.
        
        Raises UserError if:
        - No employee is linked to the current user, OR
        - The employee's `can_manage_customers` checkbox is not enabled, OR
        - The context flag `pos_controls_enforce_customer` is not set (meaning this is not a POS operation).
        
        Uses strict employee-based permissions only; user groups are NOT consulted at runtime.
        """
        if not self.env.context.get("pos_controls_enforce_customer"):
            return
        if not self.env["hr.employee"]._pos_user_has_permission("can_manage_customers"):
            raise UserError(_("You do not have permission to manage customers."))

    @api.model_create_multi
    def create(self, vals_list):
        self._ensure_pos_customer_permission()
        return super().create(vals_list)

    def write(self, vals):
        self._ensure_pos_customer_permission()
        return super().write(vals)
