
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def create_comparision(source_name, target_doc=None, ignore_permissions=True):
    docs = get_mapped_doc(
            "Quotation",
            source_name,
            {
                "Quotation": {
                    "doctype": "Comparison",
                    "field_map": {
                        "party_name": "customer",
                        "transaction_date": "start_date",
                        "taxes_and_charges": "Purchase Taxes and Charges Template",
                    },
                    "validation": {
                        "docstatus": ["=", 0],
                    },
                },
                "Quotation Item": {
				"doctype": "Comparison Item",
				"field_map": {
					"item_code": "clearance_item",
					"uom": "uom",
					"qty": "qty",
					"rate": "price",
					"amount": "total_price",
					"cost_center": "cost_center",
				},
			},
            "Sales Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges Clearances",
				"field_map": {
					"charge_type": "charge_type",
					"account_head": "account_head",
					"rate": "rate",
					"tax_amount": "tax_amount",
					"total": "total",
				},
			},
            },
            target_doc,
            postprocess=None,
            ignore_permissions=ignore_permissions,
        )

    return docs