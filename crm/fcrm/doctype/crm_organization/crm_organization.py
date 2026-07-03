# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from crm.api.exchange_rate import get_exchange_rate


class CRMOrganization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.Link | None
		annual_revenue: DF.Currency
		currency: DF.Link | None
		custom_accept_credit_card: DF.Check
		custom_clients: DF.Link | None
		custom_client_status: DF.Data | None
		custom_cost_code: DF.Data | None
		custom_country: DF.Link | None
		custom_create_deal: DF.Check
		custom_email: DF.Data | None
		custom_exact_accounting_name: DF.Data | None
		custom_first_name: DF.Data | None
		custom_invoice_projects_separately: DF.Check
		custom_last_name: DF.Data | None
		custom_phone_1: DF.Data | None
		custom_phone_2: DF.Data | None
		custom_sales_term_name: DF.Data | None
		custom_sales_unit: DF.Data | None
		custom_skype: DF.Data | None
		custom_state: DF.Data | None
		custom_tax_code_name: DF.Data | None
		exchange_rate: DF.Float
		industry: DF.Link | None
		no_of_employees: DF.Literal["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]
		organization_logo: DF.AttachImage | None
		organization_name: DF.Data | None
		territory: DF.Link | None
		website: DF.Data | None

	# end: auto-generated types

	def validate(self):
		self.update_exchange_rate()

	def after_insert(self):
		"""Runs only once when a new Organization is created."""
		try:
			contact = self.create_contact()

			if self.custom_create_deal:
				self.create_initial_deal(contact)

		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Organization Automation Failed ({self.name})"
			)
			raise

	def update_exchange_rate(self):
		if self.has_value_changed("currency") or not self.exchange_rate:
			system_currency = frappe.db.get_single_value(
				"FCRM Settings", "currency"
			) or "USD"

			exchange_rate = 1

			if self.currency and self.currency != system_currency:
				exchange_rate = get_exchange_rate(
					self.currency,
					system_currency
				)

			self.db_set("exchange_rate", exchange_rate)

	# ---------------------------------------------------------------------
	# Contact Creation
	# ---------------------------------------------------------------------

	def create_contact(self):

		existing = self.get_linked_contact()
		if existing:
			return existing

		if not any([
			self.custom_first_name,
			self.custom_last_name,
			self.custom_email,
			self.custom_phone_1,
			self.custom_phone_2,
		]):
			return None

		contact = frappe.new_doc("Contact")

		contact.first_name = self.custom_first_name or "Primary"
		contact.last_name = self.custom_last_name or ""
		contact.company_name = self.organization_name

		if self.custom_email:
			contact.email_id = self.custom_email
			contact.append(
				"email_ids",
				{
					"email_id": self.custom_email,
					"is_primary": 1,
				},
			)

		if self.custom_phone_1:
			contact.mobile_no = self.custom_phone_1
			contact.append(
				"phone_nos",
				{
					"phone": self.custom_phone_1,
					"is_primary_mobile_no": 1,
				},
			)

		if self.custom_phone_2:
			contact.phone = self.custom_phone_2
			contact.append(
				"phone_nos",
				{
					"phone": self.custom_phone_2,
					"is_primary_phone": 1,
				},
			)

		contact.append(
			"links",
			{
				"link_doctype": "CRM Organization",
				"link_name": self.name,
			},
		)

		contact.insert(ignore_permissions=True)

		return contact

	# ---------------------------------------------------------------------
	# Deal Creation
	# ---------------------------------------------------------------------

	def create_initial_deal(self, contact=None):

		deal = frappe.new_doc("CRM Deal")

		deal.organization = self.name
		deal.organization_name = self.organization_name

		if contact:
			deal.first_name = contact.first_name
			deal.last_name = contact.last_name
			deal.email = contact.email_id
			deal.mobile_no = contact.mobile_no
			deal.phone = contact.phone
		else:
			deal.first_name = self.custom_first_name
			deal.last_name = self.custom_last_name
			deal.email = self.custom_email
			deal.mobile_no = self.custom_phone_1
			deal.phone = self.custom_phone_2

		deal.website = self.website
		deal.territory = self.territory
		deal.industry = self.industry
		deal.currency = self.currency
		deal.annual_revenue = self.annual_revenue
		deal.no_of_employees = self.no_of_employees

		if hasattr(deal, "deal_owner"):
			deal.deal_owner = frappe.session.user

		deal.insert(ignore_permissions=True)

		return deal

	# ---------------------------------------------------------------------
	# Helpers
	# ---------------------------------------------------------------------

	def get_linked_contact(self):

		link = frappe.db.exists(
			"Dynamic Link",
			{
				"link_doctype": "CRM Organization",
				"link_name": self.name,
				"parenttype": "Contact",
			},
		)

		if not link:
			return None

		parent = frappe.db.get_value(
			"Dynamic Link",
			link,
			"parent",
		)

		if parent:
			return frappe.get_doc("Contact", parent)

		return None

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Organization",
				"type": "Data",
				"key": "organization_name",
				"width": "16rem",
			},
			{
				"label": "Website",
				"type": "Data",
				"key": "website",
				"width": "14rem",
			},
			{
				"label": "Industry",
				"type": "Link",
				"key": "industry",
				"options": "CRM Industry",
				"width": "14rem",
			},
			{
				"label": "Annual Revenue",
				"type": "Currency",
				"key": "annual_revenue",
				"width": "14rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]

		rows = [
			"name",
			"organization_name",
			"organization_logo",
			"website",
			"industry",
			"currency",
			"annual_revenue",
			"modified",
		]

		return {
			"columns": columns,
			"rows": rows,
		}