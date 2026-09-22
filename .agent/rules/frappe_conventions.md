# Frappe Framework Conventions

1. Use `@frappe.whitelist()` for APIs exposed to the frontend.
2. Validate permissions using `frappe.has_permission()` or `frappe.only_for()`.
3. Never bypass Frappe ORM with unescaped raw SQL.
4. Return standardized JSON responses: `{"success": true, "data": ...}`.
