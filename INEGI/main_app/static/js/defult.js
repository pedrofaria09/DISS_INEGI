$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();

});

$(function () {
    var button = $('#button_chart');
    button.click(function () {
        var chart = $('#chart_container').highcharts();
        console.log(chart);
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