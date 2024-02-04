import frappe

@frappe.whitelist(allow_guest=True)
def validate_email_mobile_combination(email, mobile):
    exists = frappe.db.exists('Member Registration', {'email': email, 'whatsapp_mobile_number': mobile})
    return {'exixts':exists}
   
