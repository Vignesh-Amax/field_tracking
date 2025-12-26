import frappe

def execute():
    if frappe.db.exists("Custom Field", "User-is_field_tracker"):
        return

    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "User",
        "fieldname": "is_field_tracker",
        "label": "Is Field Tracker",
        "fieldtype": "Check",
        "insert_after": "username",
        "default": "0"
    }).insert(ignore_permissions=True)
