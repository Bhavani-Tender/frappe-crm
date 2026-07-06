# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class Tickets(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		assign_ticket_default_is_current_user: DF.Link | None
		customer: DF.Link | None
		subject: DF.Data | None
	# end: auto-generated types
	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Subject",
				"type": "Data",
				"key": "subject",
				"width": "20rem",
			},
			{
				"label": "Customer",
				"type": "Link",
				"key": "customer",
				"options": "CRM Organization",
				"width": "16rem",
			},
			{
				"label": "Assigned To",
				"type": "Link",
				"key": "assign_ticket_default_is_current_user",
				"options": "User",
				"width": "14rem",
			},
			{
				"label": "Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "10rem",
			},
		]

		rows = [
			"name",
			"subject",
			"customer",
			"assign_ticket_default_is_current_user",
			"modified",
		]

		return {
			"columns": columns,
			"rows": rows,
		}
@frappe.whitelist()
def get_comments(ticket):
    comments = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": "Tickets",
            "reference_name": ticket,
        },
        fields=[
            "name",
            "content",
            "owner",
            "creation",
            "modified",
        ],
        order_by="creation asc",
    )

    for comment in comments:
        comment["owner_name"] = frappe.get_cached_value(
            "User",
            comment["owner"],
            "full_name",
        )

        comment["attachments"] = []

    return comments

@frappe.whitelist()
def add_comment(ticket, content):
    comment = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": "Tickets",
            "reference_name": ticket,
            "content": content,
        }
    )
    comment.insert(ignore_permissions=True)
    return comment.as_dict()

