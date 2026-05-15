# Concepts

- Permissions are employee-level checkboxes and are the runtime authority for all POS operations.
- Role groups (Shop Floor, Cashier, Supervisor, Manager) are used only as bootstrap defaults during employee creation/reassignment; they do NOT grant access at runtime.
- POS receives `pos_permissions` via `pos.session._load_pos_data()` and uses it for UI gating.
- Backend enforcement is authoritative; POS UI is a convenience layer.
- Audit logs are stored in `pos.control.audit` and are manager-only in the backend.
- If a user has no linked employee record, all POS operations fail closed with a UserError.
- Audit log UI uses a list view instead of tree for Odoo versions that disallow `tree` view types.
- The strict employee-based model ensures multi-employee and multi-user scenarios do not suffer permission bleed via group membership.
