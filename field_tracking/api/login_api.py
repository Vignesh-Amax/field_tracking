# apps/field_tracking/field_tracking/api/login_api.py
import frappe
from frappe.auth import LoginManager
import json
from frappe.utils import today


def apply_pagination(data, page=1, page_length=20):
    page = int(page) if str(page).isdigit() else 1
    page_length = int(page_length) if str(page_length).isdigit() else 20
    start = (page - 1) * page_length
    end = start + page_length
    return data[start:end], len(data)


# ====================================================================================
# API 1: Login + Basic Profile → ONLY POST
# ====================================================================================
@frappe.whitelist(allow_guest=True, methods=["POST"])
def login_get_user_profile(usr=None, pwd=None):
    # Enforce POST method (extra safety)
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)

    if not usr or not pwd:
        frappe.throw("Username and password are required", frappe.ValidationError)

    login_manager = LoginManager()
    login_manager.authenticate(user=usr, pwd=pwd)
    login_manager.post_login()

    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(f"No Employee linked to user {user}")

    emp_doc = frappe.db.get_value(
        "Employee",
        employee_id,
        ["employee_name", "designation", "department", "reports_to"],
        as_dict=True
    )

    return {
        "email": user_doc.email,
        "full_name": user_doc.full_name,
        "username": user_doc.username,
        "enabled": user_doc.enabled,
        "is_field_tracker": user_doc.get("is_field_tracker"),
        "employee_id": employee_id,
        "employee_name": emp_doc.employee_name,
        "designation": emp_doc.designation,
        "department": emp_doc.department,
        "reports_to": emp_doc.reports_to
    }


# ====================================================================================
# API 2: Agent List with Stats → ONLY GET
# ====================================================================================
@frappe.whitelist(methods=["GET"])
def get_agent_hierarchy_with_stats(page=1, page_length=20, employee_id=None, date=None):
    # Enforce GET method
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)

    self_emp_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not self_emp_id:
        frappe.throw(f"No Employee linked to user {user}")

    # Get full hierarchy under current user (including self)
    all_emp_ids_with_self = get_all_descendant_ids(self_emp_id)
    all_emp_ids = [eid for eid in all_emp_ids_with_self if eid != self_emp_id]

    if employee_id:
        if employee_id not in all_emp_ids:
            frappe.throw("Employee not found in your hierarchy", frappe.PermissionError)
        filtered_emp_ids = [employee_id]
        total_employee_count = 1
    else:
        filtered_emp_ids = all_emp_ids
        total_employee_count = len(all_emp_ids)

    employee_details = []
    if not filtered_emp_ids:
        paginated_hierarchy, total_hierarchy = [], 0
    else:
        employees = frappe.db.sql("""
            SELECT emp.name AS employee_id, emp.employee_name, emp.reports_to, emp.user_id, emp.designation
            FROM `tabEmployee` AS emp
            WHERE emp.name IN %(emp_ids)s
        """, {"emp_ids": tuple(filtered_emp_ids)}, as_dict=True)

        user_ids = [e.user_id for e in employees if e.user_id]
        target_date = date if date else today()

        latest_log_map = {}
        if user_ids:
            logs = frappe.db.sql("""
                SELECT ful.field_user, ful.latitude, ful.longitude, ful.creation,
                       ful.mobile_network, ful.battery_percentage, ful.wifi, ful.network, ful.address
                FROM `tabField User Log` ful
                WHERE ful.field_user IN %(user_ids)s
                  AND DATE(ful.creation) = %(target_date)s
                ORDER BY ful.creation DESC
            """, {"user_ids": tuple(user_ids), "target_date": target_date}, as_dict=True)

            seen = set()
            for log in logs:
                if log.field_user not in seen:
                    latest_log_map[log.field_user] = {
                        "latitude": log.latitude,
                        "longitude": log.longitude,
                        "mobile_network": log.mobile_network,
                        "battery_percentage": log.battery_percentage,
                        "wifi": log.wifi,
                        "network": log.network,
                        "address": log.address,
                        "timestamp": log.creation
                    }
                    seen.add(log.field_user)

        task_count_map = {uid: 0 for uid in user_ids}
        if user_ids:
            owner_counts = frappe.db.sql("""
                SELECT owner, COUNT(*) AS cnt
                FROM `tabField Task`
                WHERE owner IN %(user_ids)s
                GROUP BY owner
            """, {"user_ids": tuple(user_ids)}, as_dict=True)
            for row in owner_counts:
                task_count_map[row.owner] += row.cnt

            assigned_tasks = frappe.db.sql("""
                SELECT _assign
                FROM `tabField Task`
                WHERE _assign IS NOT NULL AND _assign != ''
            """, as_dict=True)

            for task in assigned_tasks:
                try:
                    assignees = json.loads(task._assign)
                    if isinstance(assignees, list):
                        for a in assignees:
                            if a in task_count_map:
                                task_count_map[a] += 1
                except (TypeError, ValueError):
                    continue

        manager_ids = list(set(e.reports_to for e in employees if e.reports_to))
        manager_map = {}
        if manager_ids:
            managers = frappe.db.sql("""
                SELECT name AS employee_id, employee_name
                FROM `tabEmployee`
                WHERE name IN %(manager_ids)s
            """, {"manager_ids": tuple(manager_ids)}, as_dict=True)
            manager_map = {m.employee_id: m.employee_name for m in managers}

        for emp in employees:
            emp_user_id = emp.user_id
            employee_details.append({
                "employee_id": emp.employee_id,
                "employee_name": emp.employee_name,
                "designation": emp.designation,
                "reports_to": emp.reports_to,
                "reports_to_employee_id": emp.reports_to,
                "reports_to_employee_name": manager_map.get(emp.reports_to),
                "latest_field_log": latest_log_map.get(emp_user_id) or None,
                "task_count": task_count_map.get(emp_user_id, 0)
            })

        paginated_hierarchy, total_hierarchy = apply_pagination(employee_details, page, page_length)

    return {
        "hierarchy_summary": {
            "total_employee_count": total_employee_count,
            "employee_details": paginated_hierarchy,
            "total": total_hierarchy,
            "page": int(page),
            "page_length": int(page_length)
        }
    }


# ====================================================================================
# API 3: Dashboard Summary → ONLY GET
# ====================================================================================
@frappe.whitelist(methods=["GET"])
def get_dashboard_summary(page=1, page_length=20):
    # Enforce GET method
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    current_user = frappe.session.user
    if current_user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)

    self_emp_id = frappe.db.get_value("Employee", {"user_id": current_user}, "name")
    if not self_emp_id:
        frappe.throw(f"No Employee linked to user {current_user}")

    all_emp_ids_with_self = get_all_descendant_ids(self_emp_id)
    all_emp_ids = [eid for eid in all_emp_ids_with_self if eid != self_emp_id]
    total_members_under_user = len(all_emp_ids)

    user_ids_for_activity = frappe.db.get_all("Employee", filters={"name": ["in", all_emp_ids_with_self]}, pluck="user_id")
    user_ids_for_activity = [u for u in user_ids_for_activity if u]
    team_user_ids = [u for u in user_ids_for_activity if u != current_user] or []
    all_user_ids_for_tasks = user_ids_for_activity  # includes current_user

    active_users_today_details = []
    if team_user_ids:
        logs = frappe.db.sql("""
            SELECT ful.*
            FROM `tabField User Log` ful
            WHERE ful.field_user IN %(user_ids)s
              AND DATE(ful.creation) = %(today)s
            ORDER BY ful.creation DESC
        """, {"user_ids": tuple(team_user_ids), "today": today()}, as_dict=True)

        seen_users = set()
        latest_logs = []
        for log in logs:
            if log.field_user not in seen_users:
                latest_logs.append(log)
                seen_users.add(log.field_user)

        emp_map = {}
        if team_user_ids:
            emps = frappe.db.sql("""
                SELECT name AS employee_id, employee_name, user_id
                FROM `tabEmployee`
                WHERE user_id IN %(user_ids)s
            """, {"user_ids": tuple(team_user_ids)}, as_dict=True)
            emp_map = {e.user_id: e for e in emps}

        for log in latest_logs:
            emp_info = emp_map.get(log.field_user, {})
            active_users_today_details.append({
                "employee_id": emp_info.get("employee_id"),
                "employee_name": emp_info.get("employee_name"),
                "user_id": log.field_user,
                "latest_field_log": log
            })

    field_user_log_today_count = len(active_users_today_details)

    owner_tasks = set(frappe.db.get_all("Field Task", filters={"owner": ["in", all_user_ids_for_tasks]}, pluck="name"))
    assigned_tasks = set()
    if all_user_ids_for_tasks:
        tasks_with_assign = frappe.db.sql("""
            SELECT name, _assign
            FROM `tabField Task`
            WHERE _assign IS NOT NULL AND _assign != ''
        """, as_dict=True)

        for task in tasks_with_assign:
            try:
                assignees = json.loads(task._assign)
                if isinstance(assignees, list) and any(a in all_user_ids_for_tasks for a in assignees):
                    assigned_tasks.add(task.name)
            except (TypeError, ValueError):
                continue

    field_task_count = len(owner_tasks | assigned_tasks)

    pending_owner_tasks = set(frappe.db.get_all("Field Task", filters={
        "owner": ["in", all_user_ids_for_tasks],
        "status": "Pending"
    }, pluck="name"))

    pending_assigned_tasks = set()
    if all_user_ids_for_tasks:
        pending_tasks_with_assign = frappe.db.sql("""
            SELECT name, _assign
            FROM `tabField Task`
            WHERE status = 'Pending'
              AND _assign IS NOT NULL AND _assign != ''
        """, as_dict=True)

        for task in pending_tasks_with_assign:
            try:
                assignees = json.loads(task._assign)
                if isinstance(assignees, list) and any(a in all_user_ids_for_tasks for a in assignees):
                    pending_assigned_tasks.add(task.name)
            except (TypeError, ValueError):
                continue

    pending_field_tasks_count = len(pending_owner_tasks | pending_assigned_tasks)

    version_activity = []
    if team_user_ids:
        versions = frappe.db.sql("""
            SELECT v.docname, v.ref_doctype AS doctype, v.data, v.owner, v.creation
            FROM `tabVersion` v
            WHERE v.ref_doctype IN ('Field Task', 'Doctor Master')
              AND v.owner IN %(user_ids)s
            ORDER BY v.creation DESC
            LIMIT 200
        """, {"user_ids": tuple(team_user_ids)}, as_dict=True)

        user_to_emp = {e.user_id: e.employee_name for e in emp_map.values()} if emp_map else {}

        for ver in versions:
            data = json.loads(ver.data) if ver.data else {}
            action = "Updated"
            changed_fields = []

            if data.get("added"):
                action = "Created"
            elif data.get("changed"):
                for change in data["changed"]:
                    if len(change) >= 3:
                        fieldname, old_value, new_value = change[0], change[1], change[2]
                        changed_fields.append({
                            "field": fieldname,
                            "old_value": old_value,
                            "new_value": new_value
                        })
                if "creation" in [c["field"] for c in changed_fields] and len(changed_fields) == 1:
                    action = "Created"
                    changed_fields = []

            version_activity.append({
                "activity_type": "version",
                "doctype": ver.doctype,
                "docname": ver.docname,
                "action": action,
                "user": ver.owner,
                "employee_name": user_to_emp.get(ver.owner),
                "timestamp": ver.creation,
                "changed_fields": changed_fields if action == "Updated" else []
            })

    field_log_activity = []
    for item in active_users_today_details:
        log = item["latest_field_log"]
        field_log_activity.append({
            "activity_type": "field_user_log",
            "doctype": "Field User Log",
            "docname": log.name,
            "action": "Checked In",
            "user": log.field_user,
            "employee_name": item["employee_name"],
            "timestamp": log.creation,
            "latitude": log.latitude,
            "longitude": log.longitude,
            "mobile_network": log.mobile_network,
            "battery_percentage": log.battery_percentage,
            "wifi": log.wifi,
            "network": log.network
        })

    all_activity = version_activity + field_log_activity
    all_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    paginated_activity, total_activity = apply_pagination(all_activity, page, page_length)

    return {
        "field_user_log_today_count": field_user_log_today_count,
        "field_task_count": field_task_count,
        "pending_field_tasks_count": pending_field_tasks_count,
        "total_members_under_user": total_members_under_user,
        "active_users_today_details": active_users_today_details,
        "recent_activity": paginated_activity,
        "total_activity": total_activity,
        "page": int(page),
        "page_length": int(page_length)
    }


# ====================================================================================
# Utility: Get all descendants in reporting hierarchy
# ====================================================================================
def get_all_descendant_ids(root_employee_id):
    all_ids = [root_employee_id]
    queue = [root_employee_id]
    while queue:
        current = queue.pop(0)
        children = frappe.db.get_all("Employee", filters={"reports_to": current}, pluck="name")
        all_ids.extend(children)
        queue.extend(children)
    return list(set(all_ids))


# ====================================================================================
# API 4: Get All Field Tasks for a Given Employee (Assigned + Owned) → ONLY GET
# ====================================================================================
# @frappe.whitelist(allow_guest=False, methods=["GET"])
# def get_field_tasks_by_employee(employee_id=None, page_length=20, page_start=0):
#     """
#     Get complete Field Task records (with all fields) for a specific employee,
#     including tasks where the employee is the owner OR assigned via _assign.
#     """
#     if frappe.request.method != "GET":
#         frappe.throw("Method not allowed", frappe.PermissionError)

#     if not employee_id:
#         frappe.throw("Employee ID is required", frappe.ValidationError)

#     # Validate employee exists and get user_id
#     user_id = frappe.db.get_value("Employee", {"name": employee_id}, "user_id")
#     if not user_id:
#         frappe.throw(f"No User linked to Employee {employee_id}", frappe.DoesNotExistError)

#     try:
#         page_length = int(page_length) if str(page_length).isdigit() else 20
#         page_start = int(page_start) if str(page_start).isdigit() else 0

#         # Step 1: Get task names where user is OWNER
#         owner_task_names = set(frappe.db.get_all("Field Task",
#                                                 filters={"owner": user_id},
#                                                 pluck="name"))

#         # Step 2: Get task names where user is ASSIGNED
#         assigned_task_names = set()
#         assigned_candidates = frappe.db.sql("""
#             SELECT name, _assign
#             FROM `tabField Task`
#             WHERE _assign IS NOT NULL AND _assign != ''
#         """, as_dict=True)

#         for task in assigned_candidates:
#             try:
#                 assignees = json.loads(task._assign)
#                 if isinstance(assignees, list) and user_id in assignees:
#                     assigned_task_names.add(task.name)
#             except (TypeError, ValueError):
#                 continue

#         # Combine both sets
#         all_task_names = list(owner_task_names | assigned_task_names)
#         total_count = len(all_task_names)

#         # Apply pagination to the list of names
#         paginated_names = all_task_names[page_start : page_start + page_length]

#         # Fetch complete documents
#         complete_data = []
#         for name in paginated_names:
#             doc = frappe.get_doc("Field Task", name)
#             complete_data.append(doc.as_dict())

#         return {
#             "employee_id": employee_id,
#             "user_id": user_id,
#             "doctype": "Field Task",
#             "data": complete_data,
#             "total_count": total_count,
#             "page_length": page_length,
#             "page_start": page_start
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), f"Error fetching tasks for employee {employee_id}")
#         frappe.throw(f"Error: {str(e)}", frappe.ValidationError)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_tasks_by_employee(employee_id=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    if not employee_id:
        frappe.throw("Employee ID is required", frappe.ValidationError)

    user_id = frappe.db.get_value("Employee", {"name": employee_id}, "user_id")
    if not user_id:
        frappe.throw(f"No User linked to Employee {employee_id}", frappe.DoesNotExistError)

    try:
        page_length = int(page_length) if str(page_length).isdigit() else 20
        page_start = int(page_start) if str(page_start).isdigit() else 0

        # Get task names
        owner_task_names = set(frappe.db.get_all("Field Task", filters={"owner": user_id}, pluck="name"))
        assigned_task_names = set()
        assigned_candidates = frappe.db.sql("""
            SELECT name, _assign
            FROM `tabField Task`
            WHERE _assign IS NOT NULL AND _assign != ''
        """, as_dict=True)

        for task in assigned_candidates:
            try:
                assignees = json.loads(task._assign)
                if isinstance(assignees, list) and user_id in assignees:
                    assigned_task_names.add(task.name)
            except (TypeError, ValueError):
                continue

        all_task_names = list(owner_task_names | assigned_task_names)
        total_count = len(all_task_names)
        paginated_names = all_task_names[page_start : page_start + page_length]

        # --- Dynamic section inference from DocType field order ---
        fields = frappe.get_all(
            "DocField",
            filters={"parent": "Field Task"},
            fields=["fieldname", "fieldtype", "label", "depends_on"],
            order_by="idx"
        )

        # Map activity_type to section labels
        ACTIVITY_TO_SECTION = {
            "Hospital Visit": "Hospital Details",
            "Distributor Visit": "Distributor Details",
            "Business Meeting": "Business Meeting Details",
            "Admin Work": None 
        }

        # Build mapping: fieldname → section_label
        field_to_section = {}
        current_section = None

        for df in fields:
            if df.fieldtype == "Section Break":
                current_section = df.label
            elif df.fieldtype == "Check":
                field_to_section[df.fieldname] = current_section

        # Reverse map: section_label → activity_type
        section_to_activity = {v: k for k, v in ACTIVITY_TO_SECTION.items() if v}

        complete_data = []
        for name in paginated_names:
            doc = frappe.get_doc("Field Task", name)
            doc_dict = doc.as_dict()

            activity_type = doc_dict.get("activity_type")
            expected_section = ACTIVITY_TO_SECTION.get(activity_type)
            subject_labels = []

            if expected_section:
                for fieldname, label in [(f, frappe.get_meta("Field Task").get_field(f).label) for f in field_to_section]:
                    if field_to_section[fieldname] == expected_section and doc_dict.get(fieldname) == 1:
                        subject_labels.append(label)

            doc_dict["subject"] = ", ".join(subject_labels)
            complete_data.append(doc_dict)

        return {
            "employee_id": employee_id,
            "user_id": user_id,
            "doctype": "Field Task",
            "data": complete_data,
            "total_count": total_count,
            "page_length": page_length,
            "page_start": page_start
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_field_tasks_by_employee for {employee_id}")
        frappe.throw(f"Error: {str(e)}", frappe.ValidationError)