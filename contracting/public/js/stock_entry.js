frappe.ui.form.on("Stock Entry", {
  refresh(frm) {
    frm.events.set_child_table_fields(frm);
    frm.events.comparison(frm);
  },
  setup: function (frm) {
    frappe.call({
      method:
        "contracting.contracting.doctype.stock_functions.fetch_contracting_data",
      callback: function (r) {
        if (r.message) {
        }
      },
    });
  },

  set_child_table_fields(frm) {
    frm.doc.items.forEach((e) => {
      var df = frappe.meta.get_docfield(
        "Stock Entry Detail",
        "comparison_item",
        e.name
      );
      df.hidden = !frm.doc.against_comparison;
    });

    frm.refresh_field("items");
  },

  against_comparison(frm) {
    frm.events.set_child_table_fields(frm);
  },
  comparison: function (frm) {
    if (frm.doc.against_comparison) {
      frappe.call({
        method:
          "contracting.contracting.doctype.stock_functions.stock_entry_setup",
        args: {
          comparison: frm.doc.comparison,
        },
        callback: function (r) {
          if (r.message) {
            frm.set_query("comparison_item", function () {
              return {
                filters: [["item_code", "in", r.message]],
              };
            });
            frm.refresh_field("comparison_item");
            frm.set_query("comparison_item", "items", function () {
              return {
                filters: [["item_code", "in", r.message]],
              };
            });
            frm.refresh_field("items");
          }
        },
      });
    }

    frm.doc.items.forEach((e) => {
      var df = frappe.meta.get_docfield(
        "Stock Entry Detail",
        "comparison_item",
        e.name
      );
      df.get_query = function () {
        var filters = {
          comparison: frm.doc.comparison || "",
        };

        return {
          query:
            "contracting.contracting.doctype.stock_entry.stock_entry.get_item_query",
          filters: filters,
        };
      };
    });
  },
  stock_entry_type : function (frm){
    frm.events.filter_stock_entry_transfer(frm)
    frm.events.set_property_domain(frm)
    // frm.events.set_field_property(frm)
  },
  set_property_domain:function(frm){
      frappe.call({
        method: "dynamic.api.get_active_domains",
        callback: function (r) {
            if (r.message && r.message.length) {
                if (r.message.includes("Contracting")) {
                  frappe.call({
                    'method': 'frappe.client.get_value',
                    'args': {
                      'doctype': 'Stock Entry Type',
                      'filters': {
                        'name': frm.doc.stock_entry_type
                      },
                       'fieldname':'purpose'
                    },
                    'callback': function(res){
                        frm.set_df_property("against_comparison", "hidden", !["Material Transfer", "Material Issue"].includes(res.message.purpose))
                        frm.refresh_field("against_comparison")
                    }
                  });
                  
                }
            }
        }
    })
      
    },
  comparison_item:function(frm){
    if(frm.doc.comparison_item){
      frappe.call({
        "method" : "contracting.contracting.doctype.stock_functions.get_comparision_items" ,
        args:{
          "comparison" : frm.doc.comparison,
          "item_code" : frm.doc.comparison_item,
        },
        callback :function(r){
          if (r.message){
            frm.clear_table("items")
            $.each(r.message || [], function(i, element) {
              let row = frm.add_child('items', {
                item_code: element.item_code,
                item_name: element.item_name,
                qty: element.total_qty,
                uom: element.uom,
                stock_uom: element.uom,
                transfer_qty: element.total_qty * element.conversion_factor,
                conversion_factor: element.conversion_factor,
                basic_rate: element.unit_price,
                
            });
            })
            frm.refresh_field("items")
          }
        } 
     
      })
    }
    

  },
});




