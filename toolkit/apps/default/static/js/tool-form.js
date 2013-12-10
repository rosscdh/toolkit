(function($) {
  $(function() {

    function calculateFilingDeadline(date) {
        date.setDate(date.getDate() + 30);

        return $.datepicker.formatDate(window.GLOBALS['JS_DATE_FORMAT'], date);
    };

    var $el = $('.datepicker[name=date_of_property_transfer]');
    $el.on('change', function() {
      $('#filing-deadline').html(calculateFilingDeadline($(this).datepicker('getDate')));
    });

    // calculate the filing deadline when page is ready
    $('#filing-deadline').html(calculateFilingDeadline($el.datepicker('getDate')));

  });
})(jQuery);
