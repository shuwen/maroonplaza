$( ".datepicker" ).datepicker({
    showOtherMonths: true,
    selectOtherMonths: true
});

$('.reveal').click(function() {
    $(this).siblings('.modal').css('display','block');
});