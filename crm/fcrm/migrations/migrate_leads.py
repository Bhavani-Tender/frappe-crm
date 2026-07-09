import re

import traceback

import frappe

from crm.fcrm.migrations.db import get_old_db


def get_lookup(cursor, table, id_field, value_field):
    cursor.execute(f"SELECT {id_field}, {value_field} FROM {table}")
    rows = cursor.fetchall()
    return {row[id_field]: row[value_field] for row in rows}


def split_name(full_name):
    if not full_name:
        return "", ""

    parts = full_name.strip().split()

    if len(parts) == 1:
        return parts[0], ""

    return parts[0], " ".join(parts[1:])

def clean_phone(phone):
    if not phone:
        return None

    phone = str(phone).strip()

    # Remove extensions like "Ext. 2332" or "x14"
    phone = re.sub(r'(?i)\s*(ext\.?|extension|x)\s*\d+$', '', phone)

    # Keep only digits, +, -, (, ), and spaces
    phone = re.sub(r'[^0-9+\-\(\)\s]', '', phone)

    phone = phone.strip()

    return phone or None

def migrate_leads():

    conn = get_old_db()

    try:
        with conn.cursor() as cursor:

            # Lookup tables from old CRM
            status_map = get_lookup(cursor, "tblleadsstatus", "id", "name")
            source_map = get_lookup(cursor, "tblleadssources", "id", "name")
            sales_unit_map = get_lookup(cursor, "tblsalesunit", "sales_id", "sale_unit")

            # Lookup tables from Frappe
            status_lookup = {
                row.lead_status: row.name
                for row in frappe.get_all(
                    "CRM Lead Status",
                    fields=["name", "lead_status"]
                )
            }

            source_lookup = {
                row.source_name: row.name
                for row in frappe.get_all(
                    "CRM Lead Source",
                    fields=["name", "source_name"]
                )
            }

            # Read all leads
            cursor.execute("SELECT * FROM tblleads")
            leads = cursor.fetchall()

            print(f"Found {len(leads)} leads")

            success = 0
            failed = 0
            skipped = 0

            for lead in leads:

                try:

                    first_name, last_name = split_name(lead["name"])

                    # Country Mapping
                    country = lead["country"] or None

                    if country and not frappe.db.exists("Country", country):
                        country = None

                    # Status Mapping
                    status = status_lookup.get(
                        status_map.get(lead["status"])
                    ) or "New Leads"

                    # Source Mapping
                    source = None

                    if lead["source"]:
                        source = source_lookup.get(
                            source_map.get(lead["source"])
                        )

                    # Duplicate Check
                    exists = False

                    if lead["email"]:
                        exists = frappe.db.exists(
                            "CRM Lead",
                            {"email": lead["email"]}
                        )
                    else:
                        exists = frappe.db.exists(
                            "CRM Lead",
                            {
                                "lead_name": lead["name"],
                                "organization": lead["company"]
                            }
                        )

                    if exists:
                        skipped += 1
                        print(f"Skipped : {lead['name']}")
                        continue
                    
                    mobile_no = clean_phone(lead["phonenumber"])
                    alternate_mobile = clean_phone(lead["phonenumber2"])

                    # Create Lead
                    doc = frappe.get_doc({
                        "doctype": "CRM Lead",

                        "lead_name": lead["name"],
                        "first_name": first_name,
                        "last_name": last_name,

                        "organization": lead["company"],

                        "email": lead["email"],

                        "mobile_no": mobile_no,
                        "custom_alternate_mobile_no": alternate_mobile,

                        "custom_skype": lead["skype"],

                        "website": lead["siteurl"],

                        "details": lead["notes"],

                        "status": status,
                        "source": source,

                        "custom_sales_unit": sales_unit_map.get(
                            lead["sales_unit"]
                        ),

                        "custom_country": country,
                        "custom_state": lead["state"],

                        "lead_owner": "Administrator",
                    })

                    doc.insert(ignore_permissions=True)

                    success += 1

                    print(f"Imported : {doc.name}")

                    # Commit every 50 records
                    if success % 50 == 0:
                        frappe.db.commit()
                        print(f"Committed {success} records...")

                except Exception:

                    failed += 1

                    print(f"\nFailed Lead ID : {lead['id']}")
                    print(f"Lead Name      : {lead['name']}")

                    traceback.print_exc()

            # Final Commit
            frappe.db.commit()

            print("\n===================================")
            print("Lead Migration Completed")
            print("===================================")
            print(f"Total Leads : {len(leads)}")
            print(f"Imported    : {success}")
            print(f"Skipped     : {skipped}")
            print(f"Failed      : {failed}")
            print("===================================")

    finally:
        conn.close()