$(document).ready(function () {

    $('input[name="begin_date_search"]').val('');
    $('input[name="begin_date_search"]').attr("placeholder","New Begin Date");
    $('input[name="end_date_search"]').val('');
    $('input[name="end_date_search"]').attr("placeholder","New End Date");

    $(function () {
        $('#formchart').submit(function() {

            var begin_date = $("#id_begin_date").val();
            var end_date = $("#id_end_date").val();

            var id_tower = $("#id_tower :selected").val();

            dataToSend = $(this).serializeArray();
            dataToSend.push({ name: 'tower_id', value: id_tower });

            if (begin_date > end_date)
                alert("Begin date is higher than end date");
            else
                $("#modal-type2").modal("show");

        });
    });

    $(function () {
        var button = $('#submit_comment');
        button.click(function () {
            var internal_comment = $("#id_internal_comment").val();
            var compact_comment = $("#id_compact_comment").val();
            var detailed_comment = $("#id_detailed_comment").val();

            dataToSend.push({ name: 'internal_comment', value: internal_comment });
            dataToSend.push({ name: 'compact_comment', value: compact_comment });
            dataToSend.push({ name: 'detailed_comment', value: detailed_comment });

            console.log(dataToSend);

            if (window.confirm("Do you really want make this action?")) {
                $.ajax({
                    url: "/classify_from_charts",
                    data: dataToSend,
                    success: function (data) {
                        if (data.is_taken) {
                            alert(data.error);
                            $("#modal-type2").modal("hide");
                        } else {
                            alert(data.message);
                            $("#modal-type2").modal("hide");
                        }
                    }
                })
            }
        });
    });


    $(function () {
        var button = $('#submit_tower');
        button.click(function () {
            if ( document.getElementById("TowerForm").classList.contains('show') ){

                var id_tower = $("#id_tower :selected").val();

                if (id_tower){
                    document.getElementById("TowerForm").classList.remove('show');
                    document.getElementById("ChartArea").classList.add('show');
                    document.getElementById("FilterForm").classList.add('show');
                    $.ajax({
                        url: "/line_highchart_json",
                        data: {tower_id: id_tower},
                        success : function(json) {
                            console.log("loading");
                            getgraph(json);
                        }
                    })
                }else
                    alert("Please choose a tower");

            } else
                document.getElementById("TowerForm").classList.add('show')
        });
    });

    $(function () {
        var button = $('#submit_new_date');
        button.click(function () {

            var id_tower = $("#id_tower :selected").val();
            var begin_date = $("#id_begin_date_search").val();
            var end_date = $("#id_end_date_search").val();

            dataToSend = {tower_id: id_tower, begin_date: begin_date, end_date: end_date};

            $.ajax({
                url: "/line_highchart_json",
                data: dataToSend,
                success : function(json) {
                    console.log("loading");
                    getgraph(json);
                }
            })
        });
    });


    $(function () {
        var button = $('#button_chart2');
        button.click(function () {
            var chart = $('#myHighChart').highcharts();
            var series = chart.series[0];
            if (series.visible) {
                $(chart.series).each(function () {
                    //this.hide();
                    this.setVisible(false, false);
                });
                chart.redraw();
                button.html('Show series');
            } else {
                $(chart.series).each(function () {
                    //this.show();
                    this.setVisible(true, false);
                });
                chart.redraw();
                button.html('Hide series');
            }
        });
    });
});

// Personalization of HighChart
function getgraph(data) {
    console.log(data);
    data["chart"] = {type: "line", 'zoomType': 'xy'};

    data["responsive"] = {
        rules: [{
            condition: {
                maxWidth: 500
            },
            chartOptions: {
                legend: {
                    layout: 'horizontal',
                    align: 'center',
                    verticalAlign: 'bottom'
                }
            }
        }]
    };

    data['tooltip'] = {xDateFormat: '%Y-%m-%d %H:%M'};

    // data['xAxis']['tickInterval'] = 24;
    data['xAxis']['type'] = 'datetime';
    data['xAxis']['labels'] = {format: '{value:%Y-%m-%d %H:%M}'};

    data['plotOptions'] = {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        // alert('Date: ' + Highcharts.dateFormat('%d/%m/%Y %H:%M:%S', this.category) + ', value: ' + this.y);
                        $("#modal-type").modal("show");

                        var date = Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.category);

                        $("#modal-type .modal-content").html(
                            "<div class='modal-header'>" +
                            "<h5 class='modal-title'>You want to add this Date ("+ date +") to?</h5>" +
                            "</div>" +
                            "<div class='modal-footer'>" +
                            "<div class='col-md-4'>" +
                            "<button type='submit' id='begin_date_modal' class='btn btn-primary btn-block'>Begin Date</button>" +
                            "</div>" +
                            "<div class='col-md-4'>" +
                            "<button type='submit' id='end_date_modal' class='btn btn-primary btn-block'>End Date</button>" +
                            "</div>" +
                            "<div class='col-md-4'>" +
                            "<button type='button' class='btn btn-warning btn-block' data-dismiss='modal'>Close</button>" +
                            "</div>" +
                            "</div>"
                        );

                        var button1 = $('#begin_date_modal');
                        button1.click(function () {
                            $("#id_begin_date").val(date);
                            $("#modal-type").modal("hide");
                        });

                        var button2 = $('#end_date_modal');
                        button2.click(function () {
                            $("#id_end_date").val(date);
                            $("#modal-type").modal("hide");
                        });
                    }
                }
            }
        }
    };

    $("#myHighChart").highcharts(data);
}