# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _load_pos_data(self, data):
        """Load POS session data with strict employee-based permissions.
        
        Permissions are derived exclusively from the employee record linked to the
        current user. If no employee is linked, this will raise a UserError.
        """
        res = super()._load_pos_data(data)
        if res.get("data"):
            try:
                permissions = self.env["hr.employee"]._pos_permissions_payload_for_user(
                    self.env.user
                )
                res["data"][0]["pos_permissions"] = permissions
            except UserError:
                # Re-raise to ensure the POS session load fails closed
                raise
        return res

    def _ensure_pos_permission(self, permission_key, action_label):
        """Check if the current user (via linked employee) has the required POS session permission.
        
        Raises UserError if:
        - No employee is linked to the current user, OR
        - The employee's checkbox for this permission is not enabled.
        
        Uses strict employee-based permissions only; user groups are NOT consulted at runtime.
        """
        if not self.env["hr.employee"]._pos_user_has_permission(permission_key):
            raise UserError(_("You do not have permission to %s.") % action_label)

    def action_pos_session_open(self):
        """Open a POS session, enforcing strict employee-based permission.
        
        Raises UserError if the current user (via linked employee) cannot open sessions.
        """
        self._ensure_pos_permission("can_open_close_session", "open POS sessions")
        res = super().action_pos_session_open()
        for session in self:
            self.env["pos.control.audit"]._log_action(
                "session_open", pos_session=session
            )
        return res

    def action_pos_session_closing_control(
        self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None
    ):
        """Close/balance a POS session, enforcing strict employee-based permission.
        
        Raises UserError if the current user (via linked employee) cannot close sessions.
        """
        self._ensure_pos_permission("can_open_close_session", "close POS sessions")
        res = super().action_pos_session_closing_control(
            balancing_account=balancing_account,
            amount_to_balance=amount_to_balance,
            bank_payment_method_diffs=bank_payment_method_diffs,
        )
        for session in self:
            self.env["pos.control.audit"]._log_action(
                "session_close", pos_session=session
            )
        return res

    def action_pos_session_close(
        self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None
    ):
        """Finalize and close a POS session, enforcing strict employee-based permission.
        
        Raises UserError if the current user (via linked employee) cannot close sessions.
        """
        self._ensure_pos_permission("can_open_close_session", "close POS sessions")
        return super().action_pos_session_close(
            balancing_account=balancing_account,
            amount_to_balance=amount_to_balance,
            bank_payment_method_diffs=bank_payment_method_diffs,
        )

    def try_cash_in_out(self, _type, amount, reason, extras):
        """Perform cash in/out in POS session, enforcing strict employee-based permission.
        
        Raises UserError if the current user (via linked employee) cannot perform cash movements.
        """
        self._ensure_pos_permission("can_cash_in_out", "perform cash in/out")
        res = super().try_cash_in_out(_type, amount, reason, extras)
        for session in self:
            note = "type=%s amount=%s reason=%s" % (_type, amount, reason)
            self.env["pos.control.audit"]._log_action(
                "cash_in_out", pos_session=session, note=note
            )
        return res
