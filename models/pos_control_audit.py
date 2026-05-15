# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosControlAudit(models.Model):
    _name = "pos.control.audit"
    _description = "POS Control Audit Log"
    _order = "create_date desc"

    action = fields.Selection(
        [
            ("payment", "Payment Processing"),
            ("order_create", "Order Creation"),
            ("discount", "Discount Application"),
            ("price_override", "Price Override"),
            ("void", "Order Cancellation / Void"),
            ("refund", "Refund"),
            ("session_open", "Session Open"),
            ("session_close", "Session Close"),
            ("report", "Reports / Sales Summary"),
            ("customer", "Customer Management"),
            ("cash_in_out", "Cash In / Out"),
        ],
        required=True,
    )
    user_id = fields.Many2one("res.users", string="User", required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    pos_order_id = fields.Many2one("pos.order", string="POS Order")
    pos_order_ref = fields.Char(string="POS Order Reference")
    pos_session_id = fields.Many2one("pos.session", string="POS Session")
    override = fields.Boolean(string="Override")
    note = fields.Char(string="Note")

    @api.model
    def _log_action(
        self,
        action,
        note=None,
        pos_order=None,
        pos_order_ref=None,
        pos_session=None,
        override=False,
    ):
        employee = self.env["hr.employee"].sudo().search(
            [("user_id", "=", self.env.uid)], limit=1
        )
        vals = {
            "action": action,
            "user_id": self.env.uid,
            "employee_id": employee.id if employee else False,
            "pos_order_id": pos_order.id if pos_order else False,
            "pos_order_ref": pos_order_ref,
            "pos_session_id": pos_session.id if pos_session else False,
            "override": bool(override),
            "note": note,
        }
        return self.sudo().create(vals)
