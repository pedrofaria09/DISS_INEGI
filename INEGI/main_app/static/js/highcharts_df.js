

// Personalization of HighChart
$.get('/line_highchart_json', function (data) {

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

    data['xAxis']['tickInterval'] = 24;
    data['xAxis']['type'] = 'datetime';
    data['xAxis']['labels'] = {format: '{value:%Y-%m-%d %H:%M}'};

    data['plotOptions'] = {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        alert('Date: ' + Highcharts.dateFormat('%d/%m/%Y %H:%M:%S', this.category) + ', value: ' + this.y);
                    }
                }
            }
        }
    };

    $("#myHighChart").highcharts(data);
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
    var button = $('#submit');
    button.click(function () {

        var begin_date = $("#id_begin_date").val();
        console.log(begin_date);
        var end_date = $("#id_end_date").val();
        console.log(end_date);

        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $.get('/line_highchart_json',
            {
                begin_date: begin_date,
                end_date: end_date
            },
            function (data, status) {
                console.log("requested access complete");
            });
        // $.ajax({
        //     url: "/line_highchart_json",
        //     data : { begin_date: begin_date, end_date: end_date},
        //     success : function(json) {
        //         console.log("requested access complete");
        //     }
        // })
    });
});