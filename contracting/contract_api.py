
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
                        "taxes_and_charges": "purchase_taxes_and_charges_template",
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
@frappe.whitelist()
def create_quotation(source_name, target_doc=None, ignore_permissions=True):
    docs = get_mapped_doc(
            "Comparison",
            source_name,
            {
                "Comparison": {
                    "doctype": "Quotation",
                    "field_map": {
                         "customer":"party_name",
                         "start_date":"transaction_date",
                        "purchase_taxes_and_charges_template": "taxes_and_charges",
                    },
                    "validation": {
                        "docstatus": ["=", 0],
                    },
                },
                "Comparison Item": {
				"doctype": "Quotation Item",
				"field_map": {
					"clearance_item":"item_code",
					"uom": "uom",
					"qty": "qty",
					"price":"rate",
					"total_price":"amount",
					"cost_center": "cost_center",
				},
			},
            "Purchase Taxes and Charges Clearances": {
				"doctype": "Sales Taxes and Charges",
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
