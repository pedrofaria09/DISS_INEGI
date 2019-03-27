$(function () {

    $(".js-create-type").click(function () {
        console.log("Equipment")
        $.ajax({
            url: '/add_type_equipment',
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-type").modal("show");
            },
            success: function (data) {
                $("#modal-type .modal-content").html(data.html_form);
            }
        });
    });

    $("#modal-type").on("submit", ".js-create-type-form", function () {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    alert("Type created!");
                    $("#modal-type").modal("hide");  // <-- Close the modal
                } else {
                    $("#modal-type .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    });

});