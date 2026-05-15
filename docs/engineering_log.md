# Engineering Log

- 2026-05-13: Initialized mobipine_odoo_pos_controls module scaffolding (manifest, models, views, assets).
- 2026-05-13: Added employee-level POS permission fields and default mapping from role groups.
- 2026-05-13: Implemented backend enforcement in pos.order, pos.session, report_saledetails, res.partner.
- 2026-05-13: Added POS UI gating patches and audit log model with manager-only access.
- 2026-05-13: Added local module category for POS Controls groups to avoid missing POS external ID.
- 2026-05-13: Removed group category fields to avoid res.groups category_id errors on this Odoo build.
- 2026-05-13: Replaced audit tree view with list view to satisfy Odoo view type validation.
- 2026-05-15: **Hardening Pass**: Made employee permissions the runtime authority. Removed group fallback from permission evaluation. All control checks now fail closed if no employee is linked to the user. Roles (via groups) remain only as bootstrap defaults during employee creation.
