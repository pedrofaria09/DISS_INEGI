$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();

});


$('.timeline2').click(function(){
    console.log(this)
});


$(document).on("click", ".timeline2", function(){
   console.log("ASDASDASD")
});