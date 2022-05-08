# Copyright (c) 2021, Dynamic and contributors
# For license information, please see license.txt

from contracting.contracting.doctype.sales_order.sales_order import set_delivery_date
from erpnext import get_default_company, get_default_cost_center
from contracting.contracting.doctype.sales_order.sales_order import is_product_bundle
from erpnext.stock.doctype.item.item import get_item_defaults
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import json
from frappe import _

from frappe.utils.data import flt, get_link_to_form, nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from six import string_types
class Comparison(Document):
	@frappe.whitelist()
	def get_cost_center(self,item_code):
		cost_center = None
		# company = get_default_company()
		if self.project :
			cost_center =  frappe.db.get_value("Project", self.project, "cost_center")
		if not cost_center and item_code :
			item = get_item_defaults(item_code,self.company )

			cost_center	= item.get("selling_cost_center")
		
		if not cost_center :
			cost_center = get_default_cost_center(self.company)
		return cost_center or ""
	def caculate_total_item_cost(self):
		self.total_cost_amount = 0 
		if self.item :
			for item in self.item :
				item.total_item_cost = float(item.qty or 0) * float(item.item_cost or 0)
				self.total_cost_amount += item.total_item_cost

	def validate(self):
		self.caculate_total_item_cost()
		self.validate_cost_centers()
		self.calc_taxes_and_totals()

	def validate_cost_centers (self):
		for item in (getattr(self,"item" , []) + getattr(self,"taxes" , [])) :
			is_group, company = frappe.get_cached_value('Cost Center',
			item.cost_center, ['is_group', 'company'])

			if company != self.company:
				frappe.throw(_("Cost Center {0} does not belong to Company {1} at row {2} in {3}")
					.format(item.cost_center, self.company , item.idx , "Items" if item.doctype=="Comparison Item" else "Taxes"))
			if is_group :
				frappe.throw(_("Cost Center {0} is Group at row {2} in {3}")
					.format(item.cost_center, item.idx , "Items" if item.doctype=="Comparison Item" else "Taxes"))
			

	def calc_taxes_and_totals(self):
		total_items = 0
		total_tax  = 0
		#### calc total items
		for item in self.item:
			total_items += float(item.qty or 0) * float(item.price or 0)
		for t in self.taxes:
			t.tax_amount = float(total_items or 0) * (t.rate /100)
			total_tax += float(t.tax_amount or 0)
			t.total =  total_items +total_tax
		grand_total = total_items + total_tax
		ins_value  = grand_total * ((self.insurance_value_rate or 0) / 100)
		delivery_ins_value = grand_total * ((self.delevery_insurance_value_rate_  or 0)/ 100)
		self.total_price = total_items
		self.tax_total   = total_tax
		self.delivery_insurance_value = delivery_ins_value
		self.insurance_value = ins_value
		self.total_insurance = ins_value + delivery_ins_value
		self.grand_total = grand_total
		self.total = grand_total


	




	@frappe.whitelist()
	def get_items(self, for_raw_material_request=0):
		items = []
		for i in self.item:
			if not i.comparison_item_card:
				items.append(dict(
					name=i.name,
					item_code=i.clearance_item,
					qty=1,
					price=i.price,
					total=i.price
				))
		return items


	#@frappe.whitelist()
	def create_insurance_payment(self,*args,**kwargs):
		from datetime import timedelta, date
		company = frappe.get_doc('Company',self.company)

		

		for item in self.insurances:
			current_date = date.today() + timedelta(days = item.vaidation_days )
			if not item.invocied:
				if item.type_of_insurance == 'For a Specified Period':
					if item.pay_method == 'Cash':
						je = self.create_journal_entry(
							debit_account = company.insurance_account_for_others_from_us,
							credit_account = company.default_cash_account,
							amount = item.amount,
							party_type="Customer",
							party=self.customer,
							debit_party = True,
							company_name = company.name
						)
						lnk = get_link_to_form(je.doctype, je.name)
						je.docstatus = 1
						je.save()
						frappe.msgprint("Journal Entry '%s' Created Successfully"%lnk)

						je2 = self.create_journal_entry(
							debit_account  = company.default_cash_account,
							credit_account = company.insurance_account_for_others_from_us ,
							amount = item.amount,
							company_name = company.name,
							posting_date = current_date,
							party_type="Customer",
							party=self.customer,
							credit_party = True,
						)
						lnk2 = get_link_to_form(je.doctype, je2.name)
						item.invocied = 1
						item.save()
						#self.insurance_payment = 1
						self.save()
						frappe.msgprint("Journal Entry '%s' Created Successfully"%lnk2)
		
					elif item.pay_method == 'Bank Guarantee':
						#try:
							doc = frappe.new_doc("Bank Guarantee")
							doc.bg_type  = 'Receiving'
							#doc.reference_doctype = "Sales Order"
							doc.start_date = date.today()
							doc.end_date  = current_date
							doc.customer = self.customer
							doc.amount = item.amount
							doc.bank  = item.bank
							doc.bank_account = item.account
							doc.validity = item.vaidation_days
							doc.margin_money = item.amount
							doc.reference_doctype = "Comparison"
							doc.reference_docname = self.name
							doc.save()
							item.bank_guarantee = doc.name
							item.invocied = 1
							item.save()
							# doc.docstatus =1
							# doc.save()
							#self.insurance_payment = 1
							self.save()
							lnk3 = get_link_to_form(doc.doctype, doc.name)
							frappe.msgprint("Bank Guarantee '%s' Created Successfully"%lnk3)
						# except Exception as ex:
						# 	print("error ======> ",str(ex))

	def create_journal_entry(self,debit_account=None,
							credit_account=None,
							party_type=None,
							party=None,
							debit_party  = False,
							credit_party = False,
							amount=0,
							company_name=None,
							posting_date=nowdate()):

		je = frappe.new_doc("Journal Entry")
		je.posting_date = posting_date
		je.voucher_type = 'Journal Entry'
		je.company = company_name
		#je.remark = f'Journal Entry against Insurance for {self.doctype} : {self.name}'

		###credit
		je.append("accounts", {
			"account": credit_account,
			"credit_in_account_currency": flt(amount),
			"reference_type": self.doctype,
			"party":party if credit_party else None,
			"party_type":party_type if credit_party else None,
			"reference_name": self.name,
			"project": self.project,
		})
		## debit
		je.append("accounts", {
			"account":   debit_account,
			"debit_in_account_currency": flt(amount),
			"reference_type": self.doctype,
			"party":party if debit_party else None,
			"party_type":party_type if debit_party else None,
			"reference_name": self.name
		})
		je.save()

		#lnk = get_link_to_form(je.doctype, je.name)
		return je


@frappe.whitelist()
def get_item_price(item_code):
	try :
		if item_code:
			
			price_list = frappe.db.sql(f"""select * from `tabItem Price` where item_code='{item_code}' and selling=1""",as_dict=1)
			print("price_list",price_list)
			if len(price_list) > 0:
				return price_list[0].price_list_rate
			return 0
	except:
		pass



@frappe.whitelist()
def make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")
		target.update({'customer': source.customer})
		target.update({'is_contracting': 1})

	doclist = get_mapped_doc("Comparison", source_name, {
		"Comparison": {
			"doctype": "Sales Order",
			# "field_map": {
			# 	"customer": "customer",
			# },
		},
		"Comparison Item": {
			"doctype": "Sales Order Item",
			"field_map": {
				"name": "sales_order_item",
				"parent": "sales_order",
				"price":"rate",
				"clearance_item":"item_code"
			},
			"add_if_empty": True
		},
		"Purchase Taxes and Charges Clearances": {
			"doctype": "Sales Taxes and Charges",
			"field_map": {
				"name": "taxes",
				"parent": "sales_order"
			},
			"add_if_empty": True
		},
	}, target_doc,postprocess, ignore_permissions=ignore_permissions)

	return doclist


@frappe.whitelist()
def make_purchase_order(source_name, selected_items=None, target_doc=None , ignore_permissions=False):
	if not selected_items: return

	if isinstance(selected_items, string_types):
		selected_items = json.loads(selected_items)

	items_to_map = [item.get('item_code') for item in selected_items if item.get('item_code') and item.get('item_code')]
	items_to_map = list(set(items_to_map))

	def set_missing_values(source, target):
		target.supplier = ""
		target.is_contracting = 1
		target.comparison = source.name
		target.down_payment_insurance_rate = source.insurance_value_rate
		target.payment_of_insurance_copy = source.delevery_insurance_value_rate_
		target.apply_discount_on = ""	
		target.additional_discount_percentage = 0.0
		target.discount_amount = 0.0
		target.inter_company_order_reference = ""
		target.customer = ""
		target.customer_name = ""
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")
        

	def update_item(source, target, source_parent):
		target.schedule_date = source_parent.end_date
		target.qty = flt(source.qty) - flt(source.purchased_qty)
		target.comparison = source_parent.name 
		target.comparison_item = source.name 


	doc = get_mapped_doc("Comparison", source_name, {
		"Comparison": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Comparison Item": {
			"doctype": "Purchase Order Item",
			"field_map": {
				"name": "purchase_order_item",
				"parent": "purchase_order",
				"price":"rate",
				"clearance_item":"item_code"
			},
			"add_if_empty": True,
			"postprocess": update_item,
			"condition": lambda doc: doc.purchased_qty < doc.qty and doc.clearance_item in items_to_map and not is_product_bundle(doc.clearance_item)
		},
		"Purchase Taxes and Charges Clearances": {
			"doctype": "Purchase Taxes and Charges",
			"field_map": {
				"name": "taxes",
				"parent": "purchase_order"
			},
			"add_if_empty": True
		},
	
	}, target_doc, set_missing_values)

	set_delivery_date(doc.items, source_name)

	return doc

@frappe.whitelist()
def create_item_cart(items,comparison,tender=None):
	items = json.loads(items).get('items')
	# print("from ifffffffffffff",items)
	# print("comparison",comparison)
	name_list = []
	for item in items:
		doc = frappe.new_doc("Comparison Item Card")
		doc.item_comparison_number = item.get("idx")
		doc.qty = 1
		doc.item_code  = item.get("item_code")
		doc.comparison = comparison
		doc.tender	   = tender
		doc.flags.ignore_mandatory = 1
		doc.save()
		name_list.append({
			"item_cart":doc.name,
			"row_id" :item.get("idx")
		})
	if name_list:
		c_doc = frappe.get_doc("Comparison",comparison)
		for n in name_list:
			for item in c_doc.item:
				if n.get("row_id") == item.get("idx"):
					item.comparison_item_card = n.get("item_cart")
		c_doc.save()
	return True



