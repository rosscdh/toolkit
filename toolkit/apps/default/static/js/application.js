// Some general UI pack related JS

// Extend JS Date with month name methods
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
    $("[data-toggle=tooltip]").tooltip("show");

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
    var datepickerSelector = '.datepicker';
    $(datepickerSelector).datepicker({
      showOtherMonths: true,
      selectOtherMonths: true,
      dateFormat: "MM d, yy",
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

    // Tweak Parsley.js forms
    var parsleySelector = '[parsley-validate]';
    $(parsleySelector).parsley({
      listeners: {
        onFormValidate: function(isFormValid, ev) {
          if (isFormValid) {
            $('.form-errors').addClass('hide');
          } else {
            var count = $('ul.parsley-error-list li').length;
            if (count > 1) {
              $('.form-errors p').html('There were ' + count + ' errors with this:');
            } else if (count == 1) {
              $('.form-errors p').html('There was 1 error with this:');
            };

            $('.form-errors').removeClass('hide');
          }
        },
        onFieldValidate: function(field) {
          var count = $('ul.parsley-error-list li').length;
          if (count > 1) {
            $('.form-errors p').html('There were ' + count + ' errors with this:');
            $('.form-errors').removeClass('hide');
          } else if (count == 1) {
            $('.form-errors p').html('There was 1 error with this:');
            $('.form-errors').removeClass('hide');
          } else {
            $('.form-errors').addClass('hide');
          };
        },
        onFieldError: function(field, constraint) {
          var count = $('ul.parsley-error-list li').length;
          if (count > 1) {
            $('.form-errors p').html('There were ' + count + ' errors with this:');
            $('.form-errors').removeClass('hide');
          } else if (count == 1) {
            $('.form-errors p').html('There was 1 error with this:');
            $('.form-errors').removeClass('hide');
          };
        }
      }
    });

    // Summernote
    $("textarea[data-toggle=summernote]").summernote({
      height: 200,
      toolbar: [
        ['style', ['bold', 'italic', 'underline', 'clear']],
        ['list', ['ul', 'ol']],
        ['para', ['paragraph']],
        ['fullscreen', ['fullscreen']]
      ],
      onblur: function() {
        var $this = $(this);
        var $el = $this.parent().siblings('textarea[data-toggle=summernote]');

        $el.html($this.code());
      }
    });

    // make code pretty
    window.prettyPrint && prettyPrint();
  });
})(jQuery);
