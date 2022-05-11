frappe.ui.form.on("Purchase Order", {
  refresh(frm) {
    frm.set_query("comparison", function () {
      return {
        filters: {
          tender_status: ["in", ["Approved"]],
        },
      };
    });
    if (frm.doc.docstatus == 1 && frm.doc.is_contracting) {
      frm.add_custom_button(
        __("Clearence"),
        function () {
          frappe.model.open_mapped_doc({
            method:
              "contracting.contracting.doctype.purchase_order.purchase_order.make_clearence_doc",
            frm: frm, //this.frm
          });
        },
        __("Create")
      );
    }
  },
});
