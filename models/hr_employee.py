# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HREmployee(models.Model):
    _inherit = "hr.employee"

    pos_can_process_payment = fields.Boolean(string="Can Process Payment")
    pos_can_create_orders = fields.Boolean(string="Can Create Orders / Add Items")
    pos_can_apply_discounts = fields.Boolean(string="Can Apply Discounts")
    pos_can_override_price = fields.Boolean(string="Can Override Price")
    pos_can_void_orders = fields.Boolean(string="Can Void / Cancel Orders")
    pos_can_process_refunds = fields.Boolean(string="Can Process Refunds")
    pos_can_open_close_session = fields.Boolean(string="Can Open / Close POS Session")
    pos_can_view_reports = fields.Boolean(string="Can View Reports / Sales Summary")
    pos_can_manage_customers = fields.Boolean(string="Can Manage Customers")
    pos_can_cash_in_out = fields.Boolean(string="Can Perform Cash In / Out")

    @api.model
    def _pos_permissions_from_groups(self, user):
        """Derive default POS permissions from user group membership.
        
        This method is used ONLY for bootstrap/seeding when creating or reassigning
        an employee record. It should NOT be used for runtime permission checks.
        Runtime permission checks must use employee checkbox fields.
        """
        is_manager = user.has_group("mobipine_odoo_pos_controls.group_pos_controls_manager")
        is_supervisor = user.has_group("mobipine_odoo_pos_controls.group_pos_controls_supervisor")
        is_cashier = user.has_group("mobipine_odoo_pos_controls.group_pos_controls_cashier")
        is_shop_floor = user.has_group("mobipine_odoo_pos_controls.group_pos_controls_shop_floor")

        return {
            "can_process_payment": bool(is_cashier or is_supervisor or is_manager),
            "can_create_orders": bool(is_shop_floor or is_cashier or is_supervisor or is_manager),
            "can_apply_discounts": bool(is_supervisor or is_manager),
            "can_override_price": bool(is_supervisor or is_manager),
            "can_void_orders": bool(is_supervisor or is_manager),
            "can_process_refunds": bool(is_manager),
            "can_open_close_session": bool(is_supervisor or is_manager),
            "can_view_reports": bool(is_supervisor or is_manager),
            "can_manage_customers": bool(is_supervisor or is_manager),
            "can_cash_in_out": bool(is_manager),
        }

    @api.model
    def _pos_permissions_payload_for_user(self, user):
        """Get POS permissions for a user based on their linked employee record.
        
        Permissions are strictly derived from the employee's checkbox fields, not from
        user group membership. If no employee record is linked, fails closed.
        """
        employee = self.sudo().search([("user_id", "=", user.id)], limit=1)
        if employee:
            return employee._pos_permissions_payload()
        # Fail closed: require explicit employee record for POS operations
        raise UserError(
            _("Employee record required for POS operations. Please contact your administrator to link an employee to this user.")
        )

    @api.model
    def _pos_user_has_permission(self, permission_key):
        permissions = self._pos_permissions_payload_for_user(self.env.user)
        return bool(permissions.get(permission_key))

    def _pos_permissions_payload(self):
        self.ensure_one()
        return {
            "can_process_payment": bool(self.pos_can_process_payment),
            "can_create_orders": bool(self.pos_can_create_orders),
            "can_apply_discounts": bool(self.pos_can_apply_discounts),
            "can_override_price": bool(self.pos_can_override_price),
            "can_void_orders": bool(self.pos_can_void_orders),
            "can_process_refunds": bool(self.pos_can_process_refunds),
            "can_open_close_session": bool(self.pos_can_open_close_session),
            "can_view_reports": bool(self.pos_can_view_reports),
            "can_manage_customers": bool(self.pos_can_manage_customers),
            "can_cash_in_out": bool(self.pos_can_cash_in_out),
        }

    def _pos_defaults_from_user(self, user):
        defaults = self._pos_permissions_from_groups(user)
        return {
            "pos_can_process_payment": defaults["can_process_payment"],
            "pos_can_create_orders": defaults["can_create_orders"],
            "pos_can_apply_discounts": defaults["can_apply_discounts"],
            "pos_can_override_price": defaults["can_override_price"],
            "pos_can_void_orders": defaults["can_void_orders"],
            "pos_can_process_refunds": defaults["can_process_refunds"],
            "pos_can_open_close_session": defaults["can_open_close_session"],
            "pos_can_view_reports": defaults["can_view_reports"],
            "pos_can_manage_customers": defaults["can_manage_customers"],
            "pos_can_cash_in_out": defaults["can_cash_in_out"],
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Create employees, seeding POS permissions from groups only if not explicitly provided."""
        for vals in vals_list:
            user_id = vals.get("user_id")
            if not user_id:
                continue
            permission_fields = [
                "pos_can_process_payment",
                "pos_can_create_orders",
                "pos_can_apply_discounts",
                "pos_can_override_price",
                "pos_can_void_orders",
                "pos_can_process_refunds",
                "pos_can_open_close_session",
                "pos_can_view_reports",
                "pos_can_manage_customers",
                "pos_can_cash_in_out",
            ]
            # Only seed from groups if NO permission fields are explicitly provided
            if any(field in vals for field in permission_fields):
                continue
            user = self.env["res.users"].browse(user_id)
            if user.exists():
                vals.update(self._pos_defaults_from_user(user))
        return super().create(vals_list)

    def write(self, vals):
        """Update employees, seeding POS permissions from groups only if user_id is changed and no explicit fields are provided."""
        if "user_id" in vals and vals.get("user_id"):
            permission_fields = {
                "pos_can_process_payment",
                "pos_can_create_orders",
                "pos_can_apply_discounts",
                "pos_can_override_price",
                "pos_can_void_orders",
                "pos_can_process_refunds",
                "pos_can_open_close_session",
                "pos_can_view_reports",
                "pos_can_manage_customers",
                "pos_can_cash_in_out",
            }
            # Only seed from groups if no explicit permission fields are provided
            if not permission_fields.intersection(vals.keys()):
                user = self.env["res.users"].browse(vals["user_id"])
                if user.exists():
                    vals.update(self._pos_defaults_from_user(user))
        return super().write(vals)
