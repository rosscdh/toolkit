;(function($){
    var oldParsley = $.fn.parsley;
    $.fn.extend({
        parsley: function(options, fn) {
            // Setup the default form listeners
            this.defaultOptions = {
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
                        };
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
            };

            var settings = $.extend({}, this.defaultOptions, options);

            return oldParsley.call(this, settings, fn);
        }
    });
    $.fn.parsley.defaults = oldParsley.defaults;
})(jQuery);
