$(function () {

    $(".js-create-type").click(function () {

        var type_data =$(this).attr('data-type');
        var string_url = null;

        if(type_data === "equipment" )
            string_url = '/add_type_equipment';

        if(type_data === "model" )
            string_url = '/add_type_model';

        if(type_data === "status" )
            string_url = '/add_type_status';

        if(type_data === "unit" )
            string_url = '/add_type_unit';

        if(type_data === "statistic" )
            string_url = '/add_type_statistic';

        if(type_data === "metric" )
            string_url = '/add_type_metric';

        if(type_data === "component" )
            string_url = '/add_type_component';

        console.log(string_url);

        $.ajax({
            url: string_url,
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