# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

# import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{"label": _("Entity"), "fieldname": "entity", "fieldtype": "Data", "width": 150},  # Teller/Branch/Corporate
		{"label": _("Pay-ins (Amount + Commission)"), "fieldname": "payins", "fieldtype": "Currency", "width": 150},
		{"label": _("Funding - Teller Till"), "fieldname": "funding_teller_till", "fieldtype": "Currency", "width": 150},
		{"label": _("Funding - Branch Vault Till"), "fieldname": "funding_branch_vault", "fieldtype": "Currency", "width": 150},
		{"label": _("Funding - Corporate Till"), "fieldname": "funding_corporate_till", "fieldtype": "Currency", "width": 150},
		{"label": _("Total Cash Inflows"), "fieldname": "total_cash_inflows", "fieldtype": "Currency", "width": 150},
	]


def get_data() -> list[dict]:
	"""Return data for the report.

	Replace the dummy data with actual aggregation queries or logic to fetch from your DB.
	"""
	return [
		# {
		# 	"date": "2025-05-27",
		# 	"entity": "Teller 001",
		# 	"payins": 12000.00,
		# 	"funding_teller_till": 2000.00,
		# 	"funding_branch_vault": 0.00,
		# 	"funding_corporate_till": 0.00,
		# 	"total_cash_inflows": 14000.00,
		# },
		# {
		# 	"date": "2025-05-27",
		# 	"entity": "Branch 01",
		# 	"payins": 18000.00,
		# 	"funding_teller_till": 0.00,
		# 	"funding_branch_vault": 3500.00,
		# 	"funding_corporate_till": 0.00,
		# 	"total_cash_inflows": 21500.00,
		# },
		# {
		# 	"date": "2025-05-27",
		# 	"entity": "Corporate HQ",
		# 	"payins": 25000.00,
		# 	"funding_teller_till": 0.00,
		# 	"funding_branch_vault": 0.00,
		# 	"funding_corporate_till": 5000.00,
		# 	"total_cash_inflows": 30000.00,
		# },
	]
