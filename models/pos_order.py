# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _ensure_pos_permission(self, permission_key, action_label):
        """Check if the current user (via linked employee) has the required POS permission.
        
        Raises UserError if:
        - No employee is linked to the current user, OR
        - The employee's checkbox for this permission is not enabled.
        
        Uses strict employee-based permissions only; user groups are NOT consulted at runtime.
        """
        if not self.env["hr.employee"]._pos_user_has_permission(permission_key):
            raise UserError(_("You do not have permission to %s.") % action_label)

    def _iter_order_line_vals(self, order):
        for line in order.get("lines", []) or []:
            if not line or len(line) < 3:
                continue
            vals = line[2] or {}
            yield vals

    def _check_pos_controls_order(self, order):
        """Enforce all POS controls for order lines: creation, discounts, price override, refunds, payment, and customer.
        
        All checks use strict employee-based permissions. If any check fails, raises UserError
        and logs the attempted action in pos.control.audit.
        """
        line_vals = list(self._iter_order_line_vals(order))
        has_lines = bool(line_vals)

        if has_lines:
            self._ensure_pos_permission("can_create_orders", "create orders")

        if order.get("partner_id"):
            self._ensure_pos_permission("can_manage_customers", "manage customers")
            self.env["pos.control.audit"]._log_action(
                "customer", pos_order_ref=order.get("name")
            )

        has_discount = any((vals.get("discount") or 0) > 0 for vals in line_vals)
        if has_discount:
            self._ensure_pos_permission("can_apply_discounts", "apply discounts")
            self.env["pos.control.audit"]._log_action(
                "discount", pos_order_ref=order.get("name")
            )

        has_price_override = any(vals.get("price_type") == "manual" for vals in line_vals)
        if has_price_override:
            self._ensure_pos_permission("can_override_price", "override prices")
            self.env["pos.control.audit"]._log_action(
                "price_override", pos_order_ref=order.get("name")
            )

        is_refund = any((vals.get("qty") or 0) < 0 for vals in line_vals)
        if is_refund:
            self._ensure_pos_permission("can_process_refunds", "process refunds")
            self.env["pos.control.audit"]._log_action(
                "refund", pos_order_ref=order.get("name")
            )

        has_payments = bool(order.get("payment_ids")) or bool(order.get("amount_paid"))
        if has_payments:
            self._ensure_pos_permission("can_process_payment", "process payments")
            is_override = not self.env.user.has_group(
                "mobipine_odoo_pos_controls.group_pos_controls_cashier"
            )
            self.env["pos.control.audit"]._log_action(
                "payment",
                pos_order_ref=order.get("name"),
                override=is_override,
            )

    def _process_order(self, order, existing_order):
        """Process POS order with strict employee-based control enforcement.
        
        Calls _check_pos_controls_order() which validates all 11 controls against
        the current user's linked employee record before allowing order processing.
        """
        self._check_pos_controls_order(order)
        return super()._process_order(order, existing_order)

    def action_pos_order_cancel(self):
        """Cancel/void a POS order, enforcing strict employee-based void permission.
        
        Raises UserError if the current user (via linked employee) cannot void orders.
        """
        self._ensure_pos_permission("can_void_orders", "cancel orders")
        res = super().action_pos_order_cancel()
        for order in self.filtered(lambda o: o.state == "cancel"):
            self.env["pos.control.audit"]._log_action("void", pos_order=order)
        return res
