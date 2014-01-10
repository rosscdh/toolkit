;(function($){
    var oldParsley = $.fn.parsley;
    $.fn.extend({
        parsley: function(options, fn) {
            // Setup the default form listeners
            this.defaultOptions = {
                errors: {
                    container: function(el) {
                        return $(el).closest('[parsley-validate]').find('.form-errors');
                    }
                },
                listeners: {
                    onFormValidate: function(isFormValid, ev) {
                        var $form = $(ev.target);
                        var $errors = $form.find('.form-errors');

                        if (isFormValid) {
                            $errors.addClass('hide');

                            // Handle remote AJAX requests
                            if ($form.data('remote')) {
                                $.ajax({
                                    type: $form.attr('method'),
                                    url: $form.attr('action'),
                                    success: function(data) {
                                        alert('ok');
                                    }
                                });

                                return false;
                            };
                        } else {
                            var count = $errors.find('ul.parsley-error-list li').length;
                            if (count > 1) {
                                $errors.find('p').html('There were ' + count + ' errors with this:');
                            } else if (count == 1) {
                                $errors.find('p').html('There was 1 error with this:');
                            };

                            $errors.removeClass('hide');
                        };
                    },
                    onFieldValidate: function(field) {
                        var $field = $(field);
                        var $form = $field.closest('[parsley-validate]');
                        var $errors = $form.find('.form-errors');

                        var count = $errors.find('ul.parsley-error-list li').length;
                        if (count > 1) {
                            $errors.find('p').html('There were ' + count + ' errors with this:');
                            $errors.removeClass('hide');
                        } else if (count == 1) {
                            $errors.find('p').html('There was 1 error with this:');
                            $errors.removeClass('hide');
                        } else {
                            $errors.addClass('hide');
                        };
                    },
                    onFieldError: function(field, constraint) {
                        var $field = $(field);
                        var $form = $field.closest('[parsley-validate]');
                        var $errors = $form.find('.form-errors');

                        var count = $errors.find('ul.parsley-error-list li').length;
                        if (count > 1) {
                            $errors.find('p').html('There were ' + count + ' errors with this:');
                            $errors.removeClass('hide');
                        } else if (count == 1) {
                            $errors.find('p').html('There was 1 error with this:');
                            $errors.removeClass('hide');
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
