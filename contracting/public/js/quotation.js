


frappe.ui.form.on("Quotation", {
    refresh: function (frm) {
        frm.add_custom_button(
            __("Make Comparision"),
            function () {
              frappe.model.open_mapped_doc({
                method: "contracting.contract_api.create_comparision",
                frm: frm, 
              });
            },
            __("Create")
          );
    }
})