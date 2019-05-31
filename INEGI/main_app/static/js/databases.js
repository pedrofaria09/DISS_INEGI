$(document).ready(function () {
    console.log("Databases");

    $(function () {
        var button = $('#dropdb_mongo');
        button.click(function () {
            console.log("dropping");
            $.ajax({
                url: "/dropdb_mongo",
                // data: {},
                success: function (data) {
                    console.log("dropped");
                }
            });
        });
    });

    $(function () {
        var button = $('#count_mongo');
        button.click(function () {
            console.log("counting");
            $.ajax({
                url: "/count_mongo",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log(data.time , ' seconds');
                }
            });
        });
    });

    $(function () {
        var button = $('#query_mg');
        button.click(function () {
            console.log("querying");
            $.ajax({
                url: "/query_mg",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log('TOTAL: ', data.time , ' seconds');
                }
            });
        });
    });

    $(function () {
        var button = $('#dropdb_influx');
        button.click(function () {
            console.log("dropping");
            $.ajax({
                url: "/dropdb_influx",
                // data: {},
                success: function (data) {
                    console.log("dropped");
                }
            });
        });
    });

    $(function () {
        var button = $('#count_influx');
        button.click(function () {
            console.log("counting");
            $.ajax({
                url: "/count_influx",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log(data.time , ' seconds');
                }
            });
        });
    });

    $(function () {
        var button = $('#query_in');
        button.click(function () {
            console.log("querying");
            $.ajax({
                url: "/query_in",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log('TOTAL: ', data.time , ' seconds');
                }
            });
        });
    });

    $(function () {
        var button = $('#dropdb_pg');
        button.click(function () {
            console.log("dropping");
            $.ajax({
                url: "/dropdb_pg",
                // data: {},
                success: function (data) {
                    console.log("dropped");
                }
            });
        });
    });

    $(function () {
        var button = $('#count_pg');
        button.click(function () {
            console.log("counting");
            $.ajax({
                url: "/count_pg",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log(data.time , ' seconds');
                }
            });
        });
    });

    $(function () {
        var button = $('#query_pg');
        button.click(function () {
            console.log("querying");
            $.ajax({
                url: "/query_pg",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log('TOTAL: ', data.time , ' seconds');
                }
            });
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

    $(function () {
        var button = $('#submit_tower');
        button.click(function () {

            var id_tower = 10;
            var begin_date = "2019-01-10 00:00";
            var end_date = "2019-01-30 00:00";

            var typeX = "files";
            // var typeX = "pg";
            // var typeX = "mo";
            // var typeX = "in";

            dataToSend = {tower_id: id_tower, begin_date: begin_date, end_date: end_date, typeX: typeX};
            ajcall();
            // var ajaxTime= new Date().getTime();
            // $.ajax({
            //     url: "/line_highchart_json_tests",
            //     data: dataToSend,
            //     // beforeSend: function (){
            //     //     var ajaxTime= new Date().getTime();
            //     // },
            //     success: function (json) {
            //         console.log("Loading Line Chart");
            //         getgraph(json);
            //         var totalTime = new Date().getTime()-ajaxTime;
            //         console.log(totalTime);
            //     }
            // });

        });
    });

    // let ajaxTime;
    // let totalTime;

    function ajcall() {
        var ajaxTime= new Date().getTime();
        $.ajax({
            url: "/line_highchart_json_tests",
            data: dataToSend,
            // beforeSend: function (){
            //     ajaxTime= new Date().getTime();
            // },
            success: function (json) {
                console.log("Loading Line Chart");
                getgraph(json);
                var totalTime = new Date().getTime()-ajaxTime;
                console.log(totalTime);
                setTimeout(ajcall, (totalTime+500))
            }
        });
    }

    function getgraph(data) {
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

        data['lang'] = {noData: "No Data to show"};
        data['noData'] = {
            style: {
                fontWeight: 'bold',
                fontSize: '15px',
                color: '#303030'
            }
        };

        data['tooltip'] = {xDateFormat: '%Y-%m-%d %H:%M'};

        // data['xAxis']['tickInterval'] = 24;
        data['xAxis']['type'] = 'datetime';
        data['xAxis']['labels'] = {format: '{value:%Y-%m-%d %H:%M}'};

        data['plotOptions'] = {
            series: {
                cursor: 'pointer',
                turboThreshold: 0,
                point: {
                    events: {
                        click: function (e) {
                            // alert('Date: ' + Highcharts.dateFormat('%d/%m/%Y %H:%M:%S', this.category) + ', value: ' + this.y);
                            $("#modal-type").modal("show");

                            var date = Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.category);

                            $("#modal-type .modal-content").html(
                                "<div class='modal-header'>" +
                                "<h5 class='modal-title'>You want to add this Date (" + date + ") to?</h5>" +
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

});