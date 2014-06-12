// Some general UI pack related JS

// Extend JS Date with month name methods
// @TODO @Jamie shoudl really be using moment.js http://momentjs.com/docs/#/get-set/month/
Date.prototype.monthNames = [
  'January', 'February', 'March',
  'April', 'May', 'June',
  'July', 'August', 'September',
  'October', 'November', 'December'
];

Date.prototype.getMonthName = function() {
  return this.monthNames[this.getMonth()];
};
Date.prototype.getShortMonthName = function() {
  return this.getMonthName().substr(0, 3);
};

// Extend JS String with repeat method
String.prototype.repeat = function(num) {
  return new Array(num + 1).join(this);
};

(function($) {
  $(function() {
    // Custom Selects
    $("select[name='state']").selectpicker({ size: 7, style: 'btn-lg btn-primary', menuStyle: 'dropdown-inverse' });

    // Tabs
    $(".nav-tabs a").on('click', function (e) {
      e.preventDefault();
      $(this).tab("show");
    })

    // Tooltips
    $("[data-toggle=tooltip]").tooltip();

    // Popover
    $("[data-toggle=popover]").popover();

    $(".auto-show").tooltip('show');

    // Tags Input
    $(".tagsinput").tagsInput();

    // Add style class name to a tooltips
    $(".tooltip").addClass(function() {
      if ($(this).prev().attr("data-tooltip-style")) {
        return "tooltip-" + $(this).prev().attr("data-tooltip-style");
      }
    });

    // Placeholders for input/textarea
    $("input, textarea").placeholder();

    // Make pagination demo work
    $(".pagination a").on('click', function() {
      $(this).parent().siblings("li").removeClass("active").end().addClass("active");
    });

    $(".btn-group a").on('click', function() {
      $(this).siblings().removeClass("active").end().addClass("active");
    });

    // Focus state for append/prepend inputs
    $('.input-group').on('focus', '.form-control', function () {
      $(this).closest('.form-group, .navbar-search').addClass('focus');
    }).on('blur', '.form-control', function () {
      $(this).closest('.form-group, .navbar-search').removeClass('focus');
    });

    // Table: Toggle all checkboxes
    $('.table .toggle-all').on('click', function() {
      var ch = $(this).find(':checkbox').prop('checked');
      $(this).closest('.table').find('tbody :checkbox').checkbox(!ch ? 'check' : 'uncheck');
    });

    // Table: Add class row selected
    $('.table tbody :checkbox').on('check uncheck toggle', function (e) {
      var $this = $(this)
        , check = $this.prop('checked')
        , toggle = e.type == 'toggle'
        , checkboxes = $('.table tbody :checkbox')
        , checkAll = checkboxes.length == checkboxes.filter(':checked').length

      $this.closest('tr')[check ? 'addClass' : 'removeClass']('selected-row');
      if (toggle) $this.closest('.table').find('.toggle-all :checkbox').checkbox(checkAll ? 'check' : 'uncheck');
    });

    // jQuery UI Datepicker
    var datepickerSelector = '[data-toggle=datepicker]';
    $(datepickerSelector).datepicker({
      showOtherMonths: true,
      selectOtherMonths: true,
      dateFormat: window.GLOBALS['JS_DATE_FORMAT'],
      yearRange: '-1:+1'
    }).prev('.btn').on('click', function (e) {
      e && e.preventDefault();
      $(datepickerSelector).focus();
    });
    $.extend($.datepicker, {_checkOffset:function(inst,offset,isFixed){return offset}});

    // Now let's align datepicker with the prepend button
    $(datepickerSelector).datepicker('widget').css({'margin-left': -$(datepickerSelector).prev('.input-group-btn').find('.btn').outerWidth()});

    // Switch
    $("[data-toggle='switch']").wrap('<div class="switch" />').parent().bootstrapSwitch();

    // Bind our overloaded version of parsley to any forms
    $('[parsley-validate]').parsley();

    // Action Buttons
    $(document).on('click.bs.action.data-api', '[data-toggle="action"]', function(e) {
      var $btn = $(this);
      var href = $btn.attr('href');
      var type = $btn.data('type');

      e.preventDefault();
      if ('redirect' == type) {
        document.location = href;
      } else if ('remote' == type) {
        var data   = $btn.data();
        var url    = href;
        var method = data['method']; delete data['method'];

        $.ajax({
          "type": method,
          "url": url,
          "data": JSON.stringify(data),
          "dataType": 'json',
          "contentType": 'application/json',
          "beforeSend": function (jqXHR, settings) {
              // Pull the token out of the DOM.
              jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]:first').val());
          },
          "complete": function ( data ) {
              document.location.reload();
          }
        });
      };
    });

    // make code pretty
    window.prettyPrint && prettyPrint();
  });
})(jQuery);
