$(function () {

    $(".js-create-type-equipment").click(function () {
        console.log("ALOOOOO")
        $.ajax({
            url: '/add_type_equipment',
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-type-equipment").modal("show");
            },
            success: function (data) {
                $("#modal-type-equipment .modal-content").html(data.html_form);
            }
        });
    });

    $("#modal-type-equipment").on("submit", ".js-create-type-equipment-form", function () {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    alert("Type created!");
                    $("#modal-type-equipment").modal("hide");  // <-- Close the modal
                } else {
                    $("#modal-type-equipment .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    });

});