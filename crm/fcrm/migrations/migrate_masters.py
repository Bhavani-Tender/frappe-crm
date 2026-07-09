import frappe

from crm.fcrm.migrations.db import get_old_db

# Map PHP CRM hex colors to Frappe CRM color names
COLOR_MAP = {
    "#28b8da": "cyan",
    "#8080ff": "blue",
    "#000000": "black",
}


def migrate_lead_status():

    conn = get_old_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM tblleadsstatus")
            rows = cursor.fetchall()

            for row in rows:

                status = row["name"].strip()

                if frappe.db.exists("CRM Lead Status", {"lead_status": status}):
                    continue

                doc = frappe.get_doc({
                    "doctype": "CRM Lead Status",
                    "lead_status": status,
                    "position": row["statusorder"] or 0,
                    "color": COLOR_MAP.get((row["color"] or "").lower(), "black"),
                })

                doc.insert(ignore_permissions=True)

            frappe.db.commit()

            print("Lead Status Migration Completed")

    finally:
        conn.close()


def migrate_lead_source():

    conn = get_old_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM tblleadssources")
            rows = cursor.fetchall()

            for row in rows:

                source = row["name"].strip()

                if frappe.db.exists("CRM Lead Source", {"source_name": source}):
                    continue

                doc = frappe.get_doc({
                    "doctype": "CRM Lead Source",
                    "source_name": source,
                    "details": "",
                })

                doc.insert(ignore_permissions=True)

            frappe.db.commit()

            print("Lead Source Migration Completed")

    finally:
        conn.close()


def migrate_masters():
    migrate_lead_status()
    migrate_lead_source()