from .doctype_api import (
    # Generic APIs
    get_doctype_fields,
    get_all_doctypes,
    get_doctype_data,
    get_doctype_complete_data,
    get_single_document,
    create_doctype_record,
    update_doctype_record,
    delete_doctype_record,
    
    # Field Task APIs
    get_field_tasks,
    get_field_tasks_complete,
    get_field_task_details,
    create_field_task,
    update_field_task,
    delete_field_task,
    
    # Doctor Master APIs
    get_doctor_masters,
    get_doctor_masters_complete,
    get_doctor_master_details,
    create_doctor_master,
    update_doctor_master,
    delete_doctor_master,
    
    # Field Task Log APIs
    get_field_task_logs,
    get_field_task_logs_complete,
    get_field_task_log_details,
    create_field_task_log,
    update_field_task_log,
    delete_field_task_log,
    
    # Field User Log APIs
    get_field_user_logs,
    get_field_user_logs_complete,
    get_field_user_log_details,
    create_field_user_log,
    update_field_user_log,
    delete_field_user_log,
    
    # Attachments File Details APIs
    get_files,
    get_files_complete,
    get_file_details,
    create_file,
    update_file,
    delete_file,
    get_files_by_reference,
    upload_file
)