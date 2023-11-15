// Copyright (c) 2021, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Comparison Item Card', {
    // onload:function(frm){
    //     // frm.ignore_doctypes_on_cancel_all = ['Comparison'];
    // },
    // refresh:function(frm){
    // },
	setup: function(frm) {
        frm.events.setup_quiries(frm)
	},
    setup_quiries:function(frm){
        frm.set_query("item", "items", function () {
            return {
              filters: [
                ["is_stock_item", "=", 1],
              ],
            };
          });
          frm.set_query("item_code", "services", function () {
            return {
              filters: [
                ["is_stock_item", "=", 0],
              ],
            };
          });
    },
    qty:(frm,cdt,cdn)=>{
      let qty =frm.doc.qty
      if(qty > frm.doc.qty_from_comparison){
          frm.set_value("qty",1)
          frappe.throw(`You cant Select QTY More Than ${frm.doc.qty_from_comparison}`)
      }
    },
    calc_stock_items_toals:(frm,cdt,cdn)=>{
         let total = 0
        let all_cost = 0
        let items = frm.doc.items
        for(let i=0 ; i<items.length ; i++){
            total += (items[i].unit_price || 0 )* (items[i].qty || 0)
        }
        all_cost  = total + (frm.doc.total_service_cost ?? 0) + (frm.doc.other_cost ?? 0)
        frm.set_value("total_item_price",total)
        frm.set_value("item_cost",total)
        frm.refresh_field("total_item_price")
        frm.refresh_field("item_cost")
        frm.set_value("total_item_cost",all_cost)
        frm.refresh_field("total_item_cost")
    },
    calc_service_items_toals:(frm,cdt,cdn)=>{
        let total    = 0
        let all_cost = 0
        let items = frm.doc.services
        for(let i=0 ; i<items.length ; i++){
            total += (items[i].unit_price || 0 )* (items[i].qty || 0)
        }
        all_cost  = total + (frm.doc.total_item_price ?? 0) + (frm.doc.other_cost ?? 0)
        frm.set_value("total_service_cost",total)
        frm.set_value("serivce_cost",total)
        frm.refresh_field("total_service_cost")
        frm.refresh_field("serivce_cost")
        frm.set_value("total_item_cost",all_cost)
        frm.refresh_field("total_item_cost")
    },
    calc_over_cost_items_toals:(frm)=>{
        let total = 0
        let all_cost = 0
        let items = frm.doc.cost
        for(let i=0 ; i<items.length ; i++){
            total += items[i].total_amount ?? 0
        }
        all_cost  = total + (frm.doc.total_item_price ?? 0) + (frm.doc.total_service_cost ?? 0)
        frm.set_value("total_cost",total)
        frm.set_value("other_cost",total)
        frm.refresh_field("total_cost")
        frm.refresh_field("other_cost")
        frm.set_value("total_item_cost",all_cost)
        frm.refresh_field("total_item_cost")
    }
    
});


frappe.ui.form.on('Comparison Item Card Stock Item', {
    item:(frm,cdt,cdn)=>{
        let row = locals[cdt][cdn]
        frm.call({
            doc: frm.doc,
            method: "get_item_details",
            args: {"item" : row.item},
            callback: function (r) {
                row.uom= r.message.weight_uom
                row.unit_price = r.message.valuation_rate
                cur_frm.refresh_field("items");
            },
         });
    },   
	unit_price:(frm,cdt,cdn)=>{
        let row = locals[cdt][cdn]
        row.total_amount = (row.qty || 0 ) *  (row.unit_price || 0)
       frm.events.calc_stock_items_toals(frm,cdt,cdn)
    },
    qty:(frm,cdt,cdn)=>{
        let row = locals[cdt][cdn]
         row.total_amount = (row.qty || 0) *  (row.unit_price || 0)
        frm.events.calc_stock_items_toals(frm,cdt,cdn)
    },
    items_remove:(frm,cdt,cdn)=>{
        frm.events.calc_stock_items_toals(frm,cdt,cdn)
    }
});

frappe.ui.form.on('Comparison Item Card Service Item', {
	unit_price:(frm,cdt,cdn)=>{
        let row = locals[cdt][cdn]
        row.total_amount = (row.qty || 0 ) *  (row.unit_price || 0)
       frm.events.calc_service_items_toals(frm,cdt,cdn)
        frm.refresh_fields("services")
    },
    qty:(frm,cdt,cdn)=>{
        let row = locals[cdt][cdn]
         row.total_amount = (row.qty || 0) *  (row.unit_price || 0)
        frm.events.calc_service_items_toals(frm,cdt,cdn)
         frm.refresh_fields("services")
    },
    services_remove:(frm,cdt,cdn)=>{
        frm.events.calc_service_items_toals(frm,cdt,cdn)
    }
});
frappe.ui.form.on('Over Cost Item', {
	total_amount:(frm,cdt,cdn)=>{
        frm.events.calc_over_cost_items_toals(frm);
    },
    cost_remove:(frm,cdt,cdn)=>{
        frm.events.calc_over_cost_items_toals(frm);
    }

});