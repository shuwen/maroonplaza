$( ".datepicker" ).datepicker({
    showOtherMonths: true,
    selectOtherMonths: true
});

$('.reveal').click(function() {
    $(this).siblings('.modal').css('display','block');
});

$('.modal-close').click(function() {
    $(this).closest('.modal').css('display','none');
});