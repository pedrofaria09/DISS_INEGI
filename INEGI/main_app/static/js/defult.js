$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();

});


$('.timeline2').click(function(){
    console.log(this)
});


$(document).on("click", ".timeline2", function(){
   console.log("ASDASDASD")
});

$(function () {

    // the button action
    $button = $('#button_chart');
    $button.click(function() {
        var chart = $('#container').highcharts();
        var series = chart.series[0];
        if (series.visible) {
            $(chart.series).each(function(){
                //this.hide();
                this.setVisible(false, false);
            });
            chart.redraw();
            $button.html('Show series');
        } else {
            $(chart.series).each(function(){
                //this.show();
                this.setVisible(true, false);
            });
            chart.redraw();
            $button.html('Hide series');
        }
    });
    $('#container').on('click', function () {
        console.log($(this).text());
    });
});