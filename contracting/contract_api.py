
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
						"docstatus": ["=", 1],
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
					"build": "build",

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
						 "project":"project",
						 "start_date":"transaction_date",
						"purchase_taxes_and_charges_template": "taxes_and_charges",
					},
					"validation": {
						"docstatus": ["=", 1],
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
					"build": "build",
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
	# frappe.errprint(f'docs-->{docs.__dict__}')


	source_doc = frappe.get_doc("Comparison", source_name)
	#get items
	for row in source_doc.item:
		#get item card
		item_card_name = frappe.db.get_value('Comparison Item Card',{'comparison':row.parent,'item_code':row.clearance_item},['name'] )
		if item_card_name:
			item_card_doc = frappe.get_doc('Comparison Item Card', item_card_name)
		# frappe.errprint(f'item_card-->{item_card_name}')
		#get child item and services for item
			if item_card_doc.items:
				for item in item_card_doc.items:
					docs.append('card_items',{
						'item':item.get("item"),
						'item_name':item.get("item_name"),
						'qty':item.get('qty'),
						'uom':item.get("uom"),
						'reference_item':row.clearance_item,
					})
			if item_card_doc.services:
				for serv in item_card_doc.services:
					docs.append('card_services',{
						'item_code':serv.get("item_code"),
						'item_name':serv.get("item_name"),
						'qty':serv.get('qty'),
						'uom':serv.get("uom"),
						'reference_item':row.clearance_item,
					})
	return docs
