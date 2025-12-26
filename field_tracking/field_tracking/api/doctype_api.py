# from frappe import _
# import frappe
# from frappe.model.document import Document
# from frappe.utils import now_datetime, cstr
# import json

# @frappe.whitelist(allow_guest=False)
# def get_doctype_fields(doctype):
#     """
#     Get all fields for a specific doctype
#     """
#     try:
#         if not doctype:
#             return {"error": "Doctype parameter is required"}
        
#         # Check if doctype exists
#         if not frappe.db.exists("DocType", doctype):
#             return {"error": f"Doctype {doctype} does not exist"}
        
#         meta = frappe.get_meta(doctype)
#         fields = []
        
#         for field in meta.fields:
#             field_info = {
#                 "fieldname": field.fieldname,
#                 "label": field.label,
#                 "fieldtype": field.fieldtype,
#                 "options": field.options,
#                 "reqd": field.reqd,
#                 "read_only": field.read_only,
#                 "hidden": field.hidden,
#                 "in_list_view": field.in_list_view,
#                 "in_standard_filter": field.in_standard_filter,
#                 "default": field.default
#             }
#             fields.append(field_info)
        
#         return {
#             "doctype": doctype,
#             "fields": fields,
#             "total_fields": len(fields)
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), f"Error getting fields for {doctype}")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False)
# def get_all_doctypes():
#     """
#     Get all custom doctypes in the Field Tracking module
#     """
#     try:
#         doctypes = frappe.get_all("DocType", 
#                                 filters={"module": "Field Tracking", "custom": 0},
#                                 fields=["name", "creation", "modified"])
        
#         return {
#             "doctypes": doctypes,
#             "total_doctypes": len(doctypes)
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Error getting Field Tracking doctypes")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False)
# def get_doctype_data(doctype, filters=None, fields=None, page_length=20, page_start=0):
#     """
#     Get data from any doctype with filtering and pagination
#     """
#     try:
#         if not doctype:
#             return {"error": "Doctype parameter is required"}
        
#         # Parse filters if provided as string
#         if filters and isinstance(filters, str):
#             try:
#                 filters = json.loads(filters)
#             except:
#                 filters = None
        
#         # Parse fields if provided as string
#         if fields and isinstance(fields, str):
#             try:
#                 fields = json.loads(fields)
#             except:
#                 fields = ["name", "creation", "modified"]
#         elif not fields:
#             fields = ["name", "creation", "modified"]
        
#         # Get data with pagination
#         data = frappe.get_all(doctype,
#                             filters=filters or {},
#                             fields=fields,
#                             limit_page_length=page_length,
#                             limit_start=page_start,
#                             order_by="creation desc")
        
#         # Get total count for pagination
#         total_count = frappe.db.count(doctype, filters=filters or {})
        
#         return {
#             "doctype": doctype,
#             "data": data,
#             "total_count": total_count,
#             "page_length": page_length,
#             "page_start": page_start
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), f"Error getting data for {doctype}")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False)
# def get_doctype_complete_data(doctype, filters=None, page_length=20, page_start=0):
#     """
#     Get COMPLETE document data for any doctype with all fields
#     """
#     try:
#         if not doctype:
#             return {"error": "Doctype parameter is required"}
        
#         # Parse filters if provided as string
#         if filters and isinstance(filters, str):
#             try:
#                 filters = json.loads(filters)
#             except:
#                 filters = None
        
#         # First get all document names with pagination
#         doc_names = frappe.get_all(doctype,
#                                  filters=filters or {},
#                                  fields=["name"],
#                                  limit_page_length=page_length,
#                                  limit_start=page_start,
#                                  order_by="creation desc")
        
#         # Get complete data for each document
#         complete_data = []
#         for doc in doc_names:
#             doc_data = frappe.get_doc(doctype, doc.name)
#             complete_data.append(doc_data.as_dict())
        
#         # Get total count for pagination
#         total_count = frappe.db.count(doctype, filters=filters or {})
        
#         return {
#             "doctype": doctype,
#             "data": complete_data,
#             "total_count": total_count,
#             "page_length": page_length,
#             "page_start": page_start
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), f"Error getting complete data for {doctype}")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False)
# def get_single_document(doctype, name):
#     """
#     Get complete single document with all fields and child tables
#     """
#     try:
#         if not doctype or not name:
#             return {"error": "Doctype and name parameters are required"}
        
#         if not frappe.db.exists(doctype, name):
#             return {"error": f"{doctype} {name} does not exist"}
        
#         doc = frappe.get_doc(doctype, name)
        
#         return {
#             "success": True,
#             "doctype": doctype,
#             "data": doc.as_dict()
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), f"Error getting document {doctype} {name}")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def create_doctype_record(doctype, data):
#     """
#     Create a new record in any doctype
#     """
#     try:
#         if not doctype or not data:
#             return {"error": "Doctype and data parameters are required"}
        
#         # Parse data if provided as string
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         # Create new document
#         doc = frappe.new_doc(doctype)
        
#         # Update fields from data
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         # Insert the document
#         doc.insert(ignore_permissions=True)
        
#         # Commit to database
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": f"{doctype} record created successfully",
#             "name": doc.name,
#             "doctype": doctype
#         }
        
#     except frappe.exceptions.ValidationError as e:
#         frappe.db.rollback()
#         return {"error": f"Validation Error: {str(e)}"}
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), f"Error creating {doctype} record")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def update_doctype_record(doctype, name, data):
#     """
#     Update an existing record in any doctype
#     """
#     try:
#         if not doctype or not name or not data:
#             return {"error": "Doctype, name and data parameters are required"}
        
#         # Parse data if provided as string
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         # Get the document
#         doc = frappe.get_doc(doctype, name)
        
#         # Update fields from data
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         # Save the document
#         doc.save(ignore_permissions=True)
        
#         # Commit to database
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": f"{doctype} record updated successfully",
#             "name": doc.name,
#             "doctype": doctype
#         }
        
#     except frappe.exceptions.DoesNotExistError:
#         frappe.db.rollback()
#         return {"error": f"{doctype} record {name} does not exist"}
#     except frappe.exceptions.ValidationError as e:
#         frappe.db.rollback()
#         return {"error": f"Validation Error: {str(e)}"}
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), f"Error updating {doctype} record")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def delete_doctype_record(doctype, name):
#     """
#     Delete a record from any doctype
#     """
#     try:
#         if not doctype or not name:
#             return {"error": "Doctype and name parameters are required"}
        
#         # Check if document exists
#         if not frappe.db.exists(doctype, name):
#             return {"error": f"{doctype} record {name} does not exist"}
        
#         # Delete the document
#         frappe.delete_doc(doctype, name, ignore_permissions=True)
        
#         # Commit to database
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": f"{doctype} record deleted successfully",
#             "name": name,
#             "doctype": doctype
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), f"Error deleting {doctype} record")
#         return {"error": str(e)}

# # ============================================================================
# # SPECIFIC APIs FOR EACH DOCTYPE - COMPLETE CRUD WITH FULL DATA
# # ============================================================================

# # Field Task APIs
# @frappe.whitelist(allow_guest=False)
# def get_field_tasks(filters=None, fields=None, page_length=20, page_start=0):
#     """Get Field Tasks with filtering"""
#     return get_doctype_data("Field Task", filters, fields, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_field_tasks_complete(filters=None, page_length=20, page_start=0):
#     """Get Field Tasks with COMPLETE data including all fields and child tables"""
#     return get_doctype_complete_data("Field Task", filters, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_field_task_details(name):
#     """Get complete single Field Task with all details"""
#     return get_single_document("Field Task", name)

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def create_field_task(data):
#     """Create a new Field Task"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.new_doc("Field Task")
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Field Task created successfully",
#             "name": doc.name,
#             "doctype": "Field Task"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error creating Field Task")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def update_field_task(name, data):
#     """Update an existing Field Task"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.get_doc("Field Task", name)
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Field Task updated successfully",
#             "name": doc.name
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error updating Field Task")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def delete_field_task(name):
#     """Delete a Field Task"""
#     return delete_doctype_record("Field Task", name)

# # Doctor Master APIs
# @frappe.whitelist(allow_guest=False)
# def get_doctor_masters(filters=None, fields=None, page_length=20, page_start=0):
#     """Get Doctor Masters with filtering"""
#     return get_doctype_data("Doctor Master", filters, fields, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_doctor_masters_complete(filters=None, page_length=20, page_start=0):
#     """Get Doctor Masters with COMPLETE data including all fields"""
#     return get_doctype_complete_data("Doctor Master", filters, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_doctor_master_details(name):
#     """Get complete single Doctor Master with all details"""
#     return get_single_document("Doctor Master", name)

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def create_doctor_master(data):
#     """Create a new Doctor Master"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.new_doc("Doctor Master")
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Doctor Master created successfully",
#             "name": doc.name,
#             "doctype": "Doctor Master"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error creating Doctor Master")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def update_doctor_master(name, data):
#     """Update an existing Doctor Master"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.get_doc("Doctor Master", name)
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Doctor Master updated successfully",
#             "name": doc.name
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error updating Doctor Master")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def delete_doctor_master(name):
#     """Delete a Doctor Master"""
#     return delete_doctype_record("Doctor Master", name)

# # Field Task Log APIs
# @frappe.whitelist(allow_guest=False)
# def get_field_task_logs(filters=None, fields=None, page_length=20, page_start=0):
#     """Get Field Task Logs with filtering"""
#     return get_doctype_data("Field Task Log", filters, fields, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_field_task_logs_complete(filters=None, page_length=20, page_start=0):
#     """Get Field Task Logs with COMPLETE data including all fields"""
#     return get_doctype_complete_data("Field Task Log", filters, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_field_task_log_details(name):
#     """Get complete single Field Task Log with all details"""
#     return get_single_document("Field Task Log", name)

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def create_field_task_log(data):
#     """Create a new Field Task Log"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.new_doc("Field Task Log")
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Field Task Log created successfully",
#             "name": doc.name,
#             "doctype": "Field Task Log"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error creating Field Task Log")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def update_field_task_log(name, data):
#     """Update an existing Field Task Log"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.get_doc("Field Task Log", name)
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Field Task Log updated successfully",
#             "name": doc.name
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error updating Field Task Log")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def delete_field_task_log(name):
#     """Delete a Field Task Log"""
#     return delete_doctype_record("Field Task Log", name)

# # Field User Log APIs (Note: Correct doctype name is "Field User Log")
# @frappe.whitelist(allow_guest=False)
# def get_field_user_logs(filters=None, fields=None, page_length=20, page_start=0):
#     """Get Field User Logs with filtering"""
#     return get_doctype_data("Field User Log", filters, fields, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_field_user_logs_complete(filters=None, page_length=20, page_start=0):
#     """Get Field User Logs with COMPLETE data including all fields"""
#     return get_doctype_complete_data("Field User Log", filters, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_field_user_log_details(name):
#     """Get complete single Field User Log with all details"""
#     return get_single_document("Field User Log", name)

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def create_field_user_log(data):
#     """Create a new Field User Log"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.new_doc("Field User Log")
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Field User Log created successfully",
#             "name": doc.name,
#             "doctype": "Field User Log"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error creating Field User Log")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def update_field_user_log(name, data):
#     """Update an existing Field User Log"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.get_doc("Field User Log", name)
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Field User Log updated successfully",
#             "name": doc.name
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error updating Field User Log")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def delete_field_user_log(name):
#     """Delete a Field User Log"""
#     return delete_doctype_record("Field User Log", name)

# # File Doctype APIs (Standard Frappe File doctype)
# @frappe.whitelist(allow_guest=False)
# def get_files(filters=None, fields=None, page_length=20, page_start=0):
#     """Get Files with filtering"""
#     return get_doctype_data("File", filters, fields, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_files_complete(filters=None, page_length=20, page_start=0):
#     """Get Files with COMPLETE data including all fields"""
#     return get_doctype_complete_data("File", filters, page_length, page_start)

# @frappe.whitelist(allow_guest=False)
# def get_file_details(name):
#     """Get complete single File with all details"""
#     return get_single_document("File", name)

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def create_file(data):
#     """Create a new File record"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.new_doc("File")
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "File created successfully",
#             "name": doc.name,
#             "doctype": "File"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error creating File")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def update_file(name, data):
#     """Update an existing File"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         doc = frappe.get_doc("File", name)
        
#         for field, value in data.items():
#             if hasattr(doc, field):
#                 setattr(doc, field, value)
        
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "File updated successfully",
#             "name": doc.name
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error updating File")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def delete_file(name):
#     """Delete a File"""
#     return delete_doctype_record("File", name)

# @frappe.whitelist(allow_guest=False)
# def get_files_by_reference(attached_to_doctype, attached_to_name, attached_to_field=None):
#     """Get files attached to a specific document"""
#     try:
#         filters = {
#             "attached_to_doctype": attached_to_doctype,
#             "attached_to_name": attached_to_name
#         }
        
#         if attached_to_field:
#             filters["attached_to_field"] = attached_to_field
        
#         files = frappe.get_all("File",
#                              filters=filters,
#                              fields=["name", "file_name", "file_url", "file_size", 
#                                     "file_type", "creation", "attached_to_field"],
#                              order_by="creation desc")
        
#         return {
#             "success": True,
#             "attached_to_doctype": attached_to_doctype,
#             "attached_to_name": attached_to_name,
#             "files": files,
#             "total_files": len(files)
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Error getting files by reference")
#         return {"error": str(e)}

# @frappe.whitelist(allow_guest=False, methods=['POST'])
# def upload_file(file_name, content, attached_to_doctype, attached_to_name, attached_to_field=None, is_private=0):
#     """Upload a new file and attach it to a document"""
#     try:
#         # Create file document
#         file_doc = frappe.new_doc("File")
#         file_doc.file_name = file_name
#         file_doc.content = content
#         file_doc.attached_to_doctype = attached_to_doctype
#         file_doc.attached_to_name = attached_to_name
#         file_doc.attached_to_field = attached_to_field
#         file_doc.is_private = is_private
        
#         file_doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "File uploaded successfully",
#             "name": file_doc.name,
#             "file_url": file_doc.file_url
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Error uploading file")
#         return {"error": str(e)}

# apps/field_tracking/field_tracking/api/doctype_api.py
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, cstr
import json


# ====================================================================================
# READ-ONLY APIs → ONLY GET
# ====================================================================================

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_doctype_fields(doctype):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype:
            return {"error": "Doctype parameter is required"}
        
        if not frappe.db.exists("DocType", doctype):
            return {"error": f"Doctype {doctype} does not exist"}
        
        meta = frappe.get_meta(doctype)
        fields = []
        
        for field in meta.fields:
            field_info = {
                "fieldname": field.fieldname,
                "label": field.label,
                "fieldtype": field.fieldtype,
                "options": field.options,
                "reqd": field.reqd,
                "read_only": field.read_only,
                "hidden": field.hidden,
                "in_list_view": field.in_list_view,
                "in_standard_filter": field.in_standard_filter,
                "default": field.default
            }
            fields.append(field_info)
        
        return {
            "doctype": doctype,
            "fields": fields,
            "total_fields": len(fields)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error getting fields for {doctype}")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_all_doctypes():
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        doctypes = frappe.get_all("DocType", 
                                filters={"module": "Field Tracking", "custom": 0},
                                fields=["name", "creation", "modified"])
        
        return {
            "doctypes": doctypes,
            "total_doctypes": len(doctypes)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error getting Field Tracking doctypes")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_doctype_data(doctype, filters=None, fields=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype:
            return {"error": "Doctype parameter is required"}
        
        if filters and isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except:
                filters = None
        
        if fields and isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except:
                fields = ["name", "creation", "modified"]
        elif not fields:
            fields = ["name", "creation", "modified"]
        
        data = frappe.get_all(doctype,
                            filters=filters or {},
                            fields=fields,
                            limit_page_length=page_length,
                            limit_start=page_start,
                            order_by="creation desc")
        
        total_count = frappe.db.count(doctype, filters=filters or {})
        
        return {
            "doctype": doctype,
            "data": data,
            "total_count": total_count,
            "page_length": page_length,
            "page_start": page_start
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error getting data for {doctype}")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_doctype_complete_data(doctype, filters=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype:
            return {"error": "Doctype parameter is required"}
        
        if filters and isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except:
                filters = None
        
        doc_names = frappe.get_all(doctype,
                                 filters=filters or {},
                                 fields=["name"],
                                 limit_page_length=page_length,
                                 limit_start=page_start,
                                 order_by="creation desc")
        
        complete_data = []
        for doc in doc_names:
            doc_data = frappe.get_doc(doctype, doc.name)
            complete_data.append(doc_data.as_dict())
        
        total_count = frappe.db.count(doctype, filters=filters or {})
        
        return {
            "doctype": doctype,
            "data": complete_data,
            "total_count": total_count,
            "page_length": page_length,
            "page_start": page_start
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error getting complete data for {doctype}")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_single_document(doctype, name):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype or not name:
            return {"error": "Doctype and name parameters are required"}
        
        if not frappe.db.exists(doctype, name):
            return {"error": f"{doctype} {name} does not exist"}
        
        doc = frappe.get_doc(doctype, name)
        
        return {
            "success": True,
            "doctype": doctype,
            "data": doc.as_dict()
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error getting document {doctype} {name}")
        return {"error": str(e)}


# ====================================================================================
# WRITE APIs → ONLY POST
# ====================================================================================

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_doctype_record(doctype, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype or not data:
            return {"error": "Doctype and data parameters are required"}
        
        if isinstance(data, str):
            data = json.loads(data)
        
        doc = frappe.new_doc(doctype)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"{doctype} record created successfully",
            "name": doc.name,
            "doctype": doctype
        }
        
    except frappe.exceptions.ValidationError as e:
        frappe.db.rollback()
        return {"error": f"Validation Error: {str(e)}"}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), f"Error creating {doctype} record")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_doctype_record(doctype, name, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype or not name or not data:
            return {"error": "Doctype, name and data parameters are required"}
        
        if isinstance(data, str):
            data = json.loads(data)
        
        doc = frappe.get_doc(doctype, name)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"{doctype} record updated successfully",
            "name": doc.name,
            "doctype": doctype
        }
        
    except frappe.exceptions.DoesNotExistError:
        frappe.db.rollback()
        return {"error": f"{doctype} record {name} does not exist"}
    except frappe.exceptions.ValidationError as e:
        frappe.db.rollback()
        return {"error": f"Validation Error: {str(e)}"}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), f"Error updating {doctype} record")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_doctype_record(doctype, name):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not doctype or not name:
            return {"error": "Doctype and name parameters are required"}
        
        if not frappe.db.exists(doctype, name):
            return {"error": f"{doctype} record {name} does not exist"}
        
        frappe.delete_doc(doctype, name, ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"{doctype} record deleted successfully",
            "name": name,
            "doctype": doctype
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), f"Error deleting {doctype} record")
        return {"error": str(e)}


# ============================================================================
# SPECIFIC DOCTYPE APIs — WITH METHOD RESTRICTIONS
# ============================================================================

# Field Task
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_tasks(filters=None, fields=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_data("Field Task", filters, fields, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_tasks_complete(filters=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_complete_data("Field Task", filters, page_length, page_start)

# @frappe.whitelist(allow_guest=False, methods=["GET"])
# def get_field_task_details(name):
#     if frappe.request.method != "GET":
#         frappe.throw("Method not allowed", frappe.PermissionError)
#     return get_single_document("Field Task", name)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_task_details(name):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)

    try:
        if not name:
            return {"error": "Name parameter is required"}
        
        if not frappe.db.exists("Field Task", name):
            return {"error": f"Field Task {name} does not exist"}
        
        # Fetch main Field Task
        task_doc = frappe.get_doc("Field Task", name)
        response_data = task_doc.as_dict()

        # Get first "In Progress" log (earliest)
        in_progress_logs = frappe.get_all(
            "Field Task Log",
            filters={"field_task": name, "status": "In Progress"},
            fields=["*"],
            order_by="creation asc",
            limit=1
        )
        response_data["in_progress_log"] = in_progress_logs[0] if in_progress_logs else None

        # Get last "Completed" log (most recent)
        completed_logs = frappe.get_all(
            "Field Task Log",
            filters={"field_task": name, "status": "Completed"},
            fields=["*"],
            order_by="creation desc",  # <-- DESC for latest
            limit=1
        )
        response_data["completed_log"] = completed_logs[0] if completed_logs else None

        return {
            "success": True,
            "doctype": "Field Task",
            "data": response_data
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error getting Field Task details for {name}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_field_task(data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.new_doc("Field Task")
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Field Task created successfully",
            "name": doc.name,
            "doctype": "Field Task"
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating Field Task")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_field_task(name, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.get_doc("Field Task", name)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Field Task updated successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error updating Field Task")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_field_task(name):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return delete_doctype_record("Field Task", name)


# Doctor Master
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_doctor_masters(filters=None, fields=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_data("Doctor Master", filters, fields, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_doctor_masters_complete(filters=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_complete_data("Doctor Master", filters, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_doctor_master_details(name):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_single_document("Doctor Master", name)

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_doctor_master(data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.new_doc("Doctor Master")
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Doctor Master created successfully",
            "name": doc.name,
            "doctype": "Doctor Master"
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating Doctor Master")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_doctor_master(name, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.get_doc("Doctor Master", name)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Doctor Master updated successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error updating Doctor Master")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_doctor_master(name):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return delete_doctype_record("Doctor Master", name)


# Field Task Log
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_task_logs(filters=None, fields=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_data("Field Task Log", filters, fields, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_task_logs_complete(filters=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_complete_data("Field Task Log", filters, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_task_log_details(name):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_single_document("Field Task Log", name)

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_field_task_log(data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.new_doc("Field Task Log")
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Field Task Log created successfully",
            "name": doc.name,
            "doctype": "Field Task Log"
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating Field Task Log")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_field_task_log(name, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.get_doc("Field Task Log", name)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Field Task Log updated successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error updating Field Task Log")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_field_task_log(name):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return delete_doctype_record("Field Task Log", name)


# Field User Log
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_user_logs(filters=None, fields=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_data("Field User Log", filters, fields, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_user_logs_complete(filters=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_complete_data("Field User Log", filters, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_field_user_log_details(name):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_single_document("Field User Log", name)

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_field_user_log(data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.new_doc("Field User Log")
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Field User Log created successfully",
            "name": doc.name,
            "doctype": "Field User Log"
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating Field User Log")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_field_user_log(name, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.get_doc("Field User Log", name)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Field User Log updated successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error updating Field User Log")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_field_user_log(name):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return delete_doctype_record("Field User Log", name)


# File APIs
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_files(filters=None, fields=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_data("File", filters, fields, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_files_complete(filters=None, page_length=20, page_start=0):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_doctype_complete_data("File", filters, page_length, page_start)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_file_details(name):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return get_single_document("File", name)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_files_by_reference(attached_to_doctype, attached_to_name, attached_to_field=None):
    if frappe.request.method != "GET":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        filters = {
            "attached_to_doctype": attached_to_doctype,
            "attached_to_name": attached_to_name
        }
        if attached_to_field:
            filters["attached_to_field"] = attached_to_field
        
        files = frappe.get_all("File",
                             filters=filters,
                             fields=["name", "file_name", "file_url", "file_size", 
                                    "file_type", "creation", "attached_to_field"],
                             order_by="creation desc")
        
        return {
            "success": True,
            "attached_to_doctype": attached_to_doctype,
            "attached_to_name": attached_to_name,
            "files": files,
            "total_files": len(files)
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error getting files by reference")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_file(data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.new_doc("File")
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "File created successfully",
            "name": doc.name,
            "doctype": "File"
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating File")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_file(name, data):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        if isinstance(data, str):
            data = json.loads(data)
        doc = frappe.get_doc("File", name)
        for field, value in data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "File updated successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error updating File")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_file(name):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    return delete_doctype_record("File", name)

@frappe.whitelist(allow_guest=False, methods=["POST"])
def upload_file(file_name, content, attached_to_doctype, attached_to_name, attached_to_field=None, is_private=0):
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed", frappe.PermissionError)
    try:
        file_doc = frappe.new_doc("File")
        file_doc.file_name = file_name
        file_doc.content = content  # Frappe handles base64 or binary via 'decode' in backend
        file_doc.attached_to_doctype = attached_to_doctype
        file_doc.attached_to_name = attached_to_name
        file_doc.attached_to_field = attached_to_field
        file_doc.is_private = is_private
        file_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "File uploaded successfully",
            "name": file_doc.name,
            "file_url": file_doc.file_url
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error uploading file")
        return {"error": str(e)}