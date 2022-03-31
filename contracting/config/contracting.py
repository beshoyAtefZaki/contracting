from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
	return [

		{
			"label": _("Main Data"),
			"items": [
				{
					"type": "doctype",
					"name": "Sales Order",
				},
				{
					"type": "doctype",
					"name": "Customer",
				},
				{
					"type": "doctype",
					"name": "Purchase Order",
				},
				{
					"type": "doctype",
					"name": "Supplier",
				},
				{
					"type": "doctype",
					"name": "Project",
				},
				{
					"type": "doctype",
					"name": "Comparison Item Card",
				},
				{
					"type": "doctype",
					"name": "Clearance State",
				},
				{
					"type": "doctype",
					"name": "Comparison Item Log",
				},
			]
		},

		{
			"label": _("Contracting"),
			"items": [
				{
					"type": "doctype",
					"name": "Project",
				},
				{
					"type": "doctype",
					"name": "Comparison",
				},
				{
					"type": "doctype",
					"name": "Tender",
				},
				{
					"type": "doctype",
					"name": "Clearance",
				},
				{
					"type": "doctype",
					"name": "Item Card",
				},
				{
					"type": "doctype",
					"name": "Comparison Item Log",
				},
			]
		}


	]
