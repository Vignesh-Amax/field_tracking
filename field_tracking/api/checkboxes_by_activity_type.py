import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def checkboxes_by_activity_type():

    ACTIVITY_TYPES = [
        "Hospital Visit",
        "Distributor Visit",
        "Business Meeting",
        "Admin Work"
    ]

    ACTIVITY_CONDITIONS = {
        act: f'eval:doc.activity_type == "{act}"' for act in ACTIVITY_TYPES
    }

    CONDITION_TO_ACTIVITY = {v: k for k, v in ACTIVITY_CONDITIONS.items()}

    result = {act: [] for act in ACTIVITY_TYPES}

    fields = frappe.get_all(
        "DocField",
        filters={"parent": "Field Task"},
        fields=["fieldname", "fieldtype", "depends_on", "fieldtype"],
        order_by="idx"
    )

    current_activity = None

    for field in fields:
        if field.fieldtype == "Section Break" and field.depends_on:
            if field.depends_on in CONDITION_TO_ACTIVITY:
                current_activity = CONDITION_TO_ACTIVITY[field.depends_on]
            else:
                current_activity = None

        elif field.fieldtype == "Check" and current_activity:
            result[current_activity].append(field.fieldname)


    return result