import frappe

from crm.fcrm.migrations.db import get_old_db


def migrate_lead_status():

    conn = get_old_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM tblleadsstatus")
            rows = cursor.fetchall()

            for row in rows:

                if frappe.db.exists("CRM Lead Status", row["name"].strip()):
                    continue

                doc = frappe.get_doc({
                    "doctype": "CRM Lead Status",
                    "name": row["name"].strip(),
                    "status": row["name"].strip(),
                })

                doc.insert(ignore_permissions=True)

            frappe.db.commit()

            print("Lead Status Imported")

    finally:
        conn.close()