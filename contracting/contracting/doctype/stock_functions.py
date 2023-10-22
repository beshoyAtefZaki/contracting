
from __future__ import unicode_literals
from frappe import _
import frappe 




#stock entry over write 

# 1- find if contatracting in installed domains 
DOMAINS = frappe.get_active_domains()
@frappe.whitelist()
def fetch_contracting_data(*args , **kwargs ):
    if 'Contracting' in DOMAINS : 
        return True
    else :
         return False


# @frappe.whitelist()
# def test(comparison , *args ,**kwargs):
#     frappe.throw('test')


@frappe.whitelist()
def stock_entry_setup(comparison , *args ,**kwargs):
    data = frappe.db.sql(""" SELECT `tabItem`.item_code  FROM  `tabItem`
    inner Join
    `tabComparison Item` on `tabItem`.name = `tabComparison Item`.clearance_item
    WHERE 
    `tabComparison Item`.parent = '%s' """%comparison )
    item_list = []
    for i in data :
        item_list.append(i[0])
    return (item_list)


#{"parent": item_code, "uom": uom}
@frappe.whitelist()
def get_comparision_items(comparison,item_code):
    data = frappe.db.sql(
    f"""SELECT `tabComparison Item Card Stock Item`.item as item_code
,`tabComparison Item Card Stock Item`.item_name
,`tabComparison Item Card Stock Item`.uom
,`tabComparison Item Card Stock Item`.qty
,`tabUOM Conversion Detail`.conversion_factor
  FROM  `tabComparison Item Card`
 INNER JOIN `tabComparison Item Card Stock Item`
 ON `tabComparison Item Card Stock Item`.parent=`tabComparison Item Card`.name
 LEFT JOIN `tabUOM Conversion Detail`
 ON `tabUOM Conversion Detail`.parent=`tabComparison Item Card Stock Item`.item 
 AND `tabUOM Conversion Detail`.uom=`tabComparison Item Card Stock Item`.uom
WHERE `tabComparison Item Card`.item_code='{item_code}' AND `tabComparison Item Card`.comparison='{comparison}'
                         """,as_dict=1)
    # print(f'\n\n\n--->{data}\n\n')
    return data or []

