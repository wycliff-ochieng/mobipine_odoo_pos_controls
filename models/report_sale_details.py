# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class ReportSaleDetails(models.AbstractModel):
    _inherit = "report.point_of_sale.report_saledetails"

    def get_sale_details(
        self, date_start=False, date_stop=False, config_ids=False, session_ids=False, **kwargs
    ):
        """Retrieve POS/sales report details, enforcing strict employee-based report permission.
        
        Raises UserError if the current user (via linked employee) cannot view reports.
        Uses strict employee-based permissions only; user groups are NOT consulted at runtime.
        """
        if not self.env["hr.employee"]._pos_user_has_permission("can_view_reports"):
            raise UserError(_("You do not have permission to view reports."))
        self.env["pos.control.audit"]._log_action("report")
        return super().get_sale_details(
            date_start=date_start,
            date_stop=date_stop,
            config_ids=config_ids,
            session_ids=session_ids,
            **kwargs,
        )
