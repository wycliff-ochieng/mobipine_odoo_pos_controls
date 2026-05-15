**Odoo Point of Sale**

Employee-Level Access Controls

**1\. Overview**
================

This document defines the access control requirements for the Odoo Point of Sale (POS) system, modelled around the operational structure of a Kenyan supermarket environment. 

The core principle is a clear separation of duties — the employee who assists with a sale is not necessarily the one who receives payment, and sensitive actions are restricted to authorized roles only.

All controls should be configured at the Employee level using a checkbox-based permissions model. 

This provides flexibility — roles serve as labels, while checkboxes govern what each employee can actually do at the POS.

**2\. Employee Roles**
======================

**Role**

**Responsibility**

**Shop Floor Staff**

Assists customers, creates orders, adds items to POS

**Cashier**

Stationed at the till; primary payment processor

**Supervisor**

Oversees staff; approves discounts, voids, overrides

**Manager**

Full oversight; refunds, reports, cash in/out, session control

**3\. POS Access Controls**
===========================

The table below defines all eleven (11) controls, who can perform each action, any override exceptions, and how the POS interface responds for unauthorized employees.

**#**

**Control**

**Who Can Perform**

**Override / Exception**

**UI Visibility**

**1**

**Payment Processing**

Cashier only can process payments

Supervisor / Manager can process in exceptional cases — this should be logged as override

Button visible to all; non-cashiers blocked with warning/error message

**2**

**Order Creation & Item Entry**

Shop Floor Staff and above

—

Hidden from unauthorized employees

**3**

**Discount Application**

Supervisor and above

—

Hidden if checkbox not enabled

**4**

**Price Override**

Supervisor and above

—

Hidden if checkbox not enabled

**5**

**Order Cancellation / Void**

Supervisor and above

—

Hidden if checkbox not enabled

**6**

**Refunds**

Manager only

—

Hidden if checkbox not enabled

**7**

**POS Session Open / Close**

Manager or Supervisor

A specifically designated employee can also be granted this right

Hidden if checkbox not enabled

**8**

**Reports / Sales Summary**

Manager and Supervisor

—

Hidden if checkbox not enabled

**9**

**Customer Management**

Configurable via checkbox at employee level

Any employee can be granted this right

Hidden if checkbox not enabled

**10**

**Cash In / Cash Out**

Manager only

—

Hidden if checkbox not enabled

**11**

**Audit / Activity Log**

Manager can view all override and sensitive action logs

Every sensitive action is logged against the employee who performed it

Backend access only

**4\. Employee Checkbox Configuration**
=======================================

Each employee record will carry a dedicated POS Permissions section containing the following checkboxes. The table below shows the recommended default configuration per role. These can be adjusted per employee as needed.

**Permission**

**Shop Floor**

**Cashier**

**Supervisor**

**Manager**

Can Process Payment

—

**✓**

**✓**

**✓**

Can Create Orders / Add Items

**✓**

**✓**

**✓**

**✓**

Can Apply Discounts

—

—

**✓**

**✓**

Can Override Price

—

—

**✓**

**✓**

Can Void / Cancel Orders

—

—

**✓**

**✓**

Can Process Refunds

—

—

—

**✓**

Can Open / Close POS Session

—

—

**✓**

**✓**

Can View Reports / Sales Summary

—

—

**✓**

**✓**

Can Manage Customers

—

—

**✓**

**✓**

Can Perform Cash In / Out

—

—

—

**✓**

**5. Implementation Mapping (Odoo 19)**
=====================================

This module implements the controls above with **both backend validation and POS UI gating**, while keeping the module standalone (depends only on `point_of_sale` and `hr`).

**Backend enforcement points**

- **Order creation & item entry**: `pos.order._process_order()` blocks when order lines exist and `Can Create Orders` is unchecked.
- **Payment processing**: `pos.order._process_order()` blocks when payment lines exist and `Can Process Payment` is unchecked; non-cashier payment use is logged as an override.
- **Discounts**: `pos.order._process_order()` blocks if any order line has `discount > 0` without permission.
- **Price override**: `pos.order._process_order()` blocks if any order line has `price_type = manual` without permission.
- **Order cancellation / void**: `pos.order.action_pos_order_cancel()` blocks without permission.
- **Refunds**: `pos.order._process_order()` blocks if any line quantity is negative without permission.
- **Session open / close**: `pos.session.action_pos_session_open()` and `pos.session.action_pos_session_closing_control()` block without permission.
- **Cash in / out**: `pos.session.try_cash_in_out()` blocks without permission.
- **Reports / sales summary**: `report.point_of_sale.report_saledetails.get_sale_details()` blocks without permission.
- **Customer management**: `res.partner.create/write()` blocks when invoked from POS with `pos_controls_enforce_customer` context and permission is missing; POS order submission with a `partner_id` also checks permission.

**POS UI gating**

- Payment actions hidden unless `Can Process Payment`.
- Refund and cancel buttons hidden unless permitted.
- Cash in/out and reports menu items hidden unless permitted.
- Customer selector hidden unless permitted.
- Numpad discount/price buttons disabled unless permitted.
- POS actions also show a warning dialog when attempted without permission.

**Audit / activity log**

- All sensitive actions create records in `pos.control.audit`.
- Read access is restricted to POS Manager role in the backend.