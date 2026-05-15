# Postmortem

- 2026-05-13: Install failed due to missing POS category XML ID; fixed by adding local module category.
- 2026-05-13: Install failed due to invalid res.groups category_id; fixed by removing category fields.
- 2026-05-13: Install failed due to tree view type; fixed by switching audit list view to `list`.
- 2026-05-15: Permission controls were loose when multiple employees and users existed due to runtime group fallback. Hardening pass removed group fallback from all runtime permission checks. Permissions now derive exclusively from employee checkbox values or fail closed.
