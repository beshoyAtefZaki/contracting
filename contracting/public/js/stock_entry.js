frappe.ui.form.on("Stock Entry", {
  refresh(frm) {
    // your code here

    frm.events.set_child_table_fields(frm);
    frm.events.comparison(frm);
  },
  setup: function (frm) {
    frappe.call({
      method:
        "contracting.contracting.doctype.stock_functions.fetch_contracting_data",
      callback: function (r) {
        console.log(r);
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
});
