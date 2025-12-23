# import frappe
# from frappe import _

# @frappe.whitelist(allow_guest=False)
# def get_all_field_tasks():
#     """
#     POST-only API to fetch all Field Task records.
#     Works even with empty body (e.g., simple POST from Postman).
#     Supports optional pagination via JSON body (if provided).
#     """
#     if frappe.request.method != "POST":
#         frappe.throw(_("Method not allowed"), frappe.DoesNotExistError)

#     # Safely get JSON if present, else use defaults
#     try:
#         json_data = frappe.request.json or {}
#     except Exception:
#         json_data = {}

#     page_length = int(json_data.get("page_length", 20))
#     page = int(json_data.get("page", 1))
#     filters = json_data.get("filters", {})

#     if not isinstance(filters, dict):
#         frappe.throw(_("'filters' must be a JSON object."))

#     # Fetch records
#     tasks = frappe.get_all(
#         "Field Task",
#         filters=filters,
#         fields=["name", "activity_type", "status", "hospital", "doctor", "modified", "owner"],
#         order_by="modified desc",
#         limit_page_length=page_length,
#         limit_start=(page - 1) * page_length
#     )
#     total = frappe.db.count("Field Task", filters=filters)

#     return {
#         "status": "success",
#         "data": tasks,
#         "total": total,
#         "page": page,
#         "page_length": page_length,
#         "has_more": len(tasks) >= page_length
#     }

# @frappe.whitelist(allow_guest=False)
# def update_field_task():
#     """
#     POST-only API to update a Field Task.
#     Expects JSON body with 'name' and 'update_data'.
#     Example:
#     {
#         "name": "F-TASK-2025-00012",
#         "update_data": {
#             "status": "Completed",
#             "is_join": 1,
#             "join_employee": "HR-EMP-00002"
#         }
#     }
#     """
#     if frappe.request.method != "POST":
#         frappe.throw(_("Method not allowed"), frappe.DoesNotExistError)

#     json_data = frappe.request.json
#     if not json_data:
#         frappe.throw(_("JSON payload is required."))

#     docname = json_data.get("name")
#     update_data = json_data.get("update_data")

#     if not docname:
#         frappe.throw(_("Field Task 'name' is required."))
#     if not isinstance(update_data, dict):
#         frappe.throw(_("'update_data' must be a JSON object."))

#     if not frappe.db.exists("Field Task", docname):
#         frappe.throw(_("Field Task {0} not found.").format(frappe.bold(docname)))

#     doc = frappe.get_doc("Field Task", docname)
#     valid_fields = {f.fieldname for f in doc.meta.fields}

#     for key, value in update_data.items():
#         if key not in valid_fields:
#             frappe.throw(_("Field '{0}' does not exist in Field Task.").format(key))
#         doc.set(key, value)

#     doc.save(ignore_permissions=False)
#     frappe.db.commit()

#     return {
#         "status": "success",
#         "message": _("Field Task {0} updated successfully.").format(docname),
#         "name": doc.name
#     }

import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_all_field_tasks():
    """
    POST-only API to fetch all Field Task records with all fields and child tables.
    Supports optional pagination via JSON body:
    {
        "page": 1,
        "page_length": 20,
        "filters": { ... }
    }
    """
    if frappe.request.method != "POST":
        frappe.throw(_("Method not allowed"), frappe.DoesNotExistError)

    # Parse JSON safely if sent; otherwise use defaults
    json_data = {}
    if frappe.request.content_type and "application/json" in frappe.request.content_type:
        try:
            json_data = frappe.request.json or {}
        except Exception:
            pass  # Ignore invalid JSON, use empty dict

    page_length = int(json_data.get("page_length", 20))
    page = int(json_data.get("page", 1))
    filters = json_data.get("filters", {})

    if not isinstance(filters, dict):
        frappe.throw(_("'filters' must be a JSON object."))

    # Fetch full documents (including child tables)
    tasks = frappe.get_all(
        "Field Task",
        filters=filters,
        fields=["*"],  # All fields
        order_by="modified desc",
        limit_page_length=page_length,
        limit_start=(page - 1) * page_length,
        ignore_permissions=False
    )

    # Enhance with child table data (e.g., attachments_file_details)
    full_tasks = []
    for task in tasks:
        doc = frappe.get_doc("Field Task", task.name)
        full_tasks.append(doc.as_dict())

    total = frappe.db.count("Field Task", filters=filters)

    return {
        "status": "success",
        "data": full_tasks,
        "total": total,
        "page": page,
        "page_length": page_length,
        "has_more": len(full_tasks) >= page_length
    }

@frappe.whitelist(allow_guest=False)
def update_field_task():
    """
    POST-only API to update a Field Task.
    Expects:
    {
        "name": "F-TASK-2025-00012",
        "update_data": {
            "status": "Completed",
            "is_join": 1,
            "join_employee": "HR-EMP-00002"
        }
    }
    """
    if frappe.request.method != "POST":
        frappe.throw(_("Method not allowed"), frappe.DoesNotExistError)

    if not frappe.request.json:
        frappe.throw(_("JSON payload is required."))

    json_data = frappe.request.json
    docname = json_data.get("name")
    update_data = json_data.get("update_data")

    if not docname:
        frappe.throw(_("Field Task 'name' is required."))
    if not isinstance(update_data, dict):
        frappe.throw(_("'update_data' must be a JSON object."))

    if not frappe.db.exists("Field Task", docname):
        frappe.throw(_("Field Task {0} not found.").format(frappe.bold(docname)))

    doc = frappe.get_doc("Field Task", docname)
    valid_fields = {f.fieldname for f in doc.meta.fields}

    for key, value in update_data.items():
        if key not in valid_fields:
            frappe.throw(_("Field '{0}' does not exist in Field Task.").format(key))
        doc.set(key, value)

    doc.save(ignore_permissions=False)
    frappe.db.commit()

    return {
        "status": "success",
        "message": _("Field Task {0} updated successfully.").format(docname),
        "name": doc.name
    }