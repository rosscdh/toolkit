;(function($){
    var oldParsley = $.fn.parsley;
    $.fn.extend({
        parsley: function(options, fn) {
            /* Setup the default form listeners */
            this.defaultOptions = {
                animate: false,
                scrollDuration: 0,
                errors: {
                    container: function(el) {
                        return $(el).closest('[parsley-validate]').find('.parsley-errors');
                    }
                },
                listeners: {
                    onFormValidate: function(isFormValid, ev, ParsleyForm) {
                        var $form           = $(ev.target);
                        var $errors         = ParsleyForm.options.errorContainer || ParsleyForm.options.errors.container(ParsleyForm.$element);
                        var $errorContainer = $errors.closest('.form-errors');

                        var hash       = 'parsley-ajax-error-list';
                        var ulError    = '#' + hash;
                        var ulTemplate = $(ParsleyForm.options.errors.errorsWrapper).attr('id', hash).addClass('parsley-error-list');

                        /* remove any ajax errors */
                        $(ulError).remove();

                        if (isFormValid) {
                            $errorContainer.addClass('hide');

                            /* Handle remote AJAX requests */
                            if ($form.data('remote')) {
                                $.ajax({
                                    data: $form.serialize(),
                                    dataType: 'json',
                                    headers: {
                                        'X-CSRFToken': $form.find('input[name=csrfmiddlewaretoken]').val()
                                    },
                                    type: $form.attr('method'),
                                    url: $form.attr('action'),
                                    beforeSend: function () {
                                        // disable the button
                                        $form.find('input[name=submit]').prop('disabled', true);
                                        $form.find('input[type=submit]').prop('disabled', true);
                                    },
                                    error: function(data) {
                                        var payload = data.responseJSON;

                                        var count = $(payload['errors']).length;
                                        if (count > 1) {
                                            $errorContainer.find('p').html('There were ' + count + ' errors with this:');
                                        } else if (count == 1) {
                                            $errorContainer.find('p').html('There was 1 error with this:');
                                        };

                                        $errors.append(ParsleyForm.options.animate ? ulTemplate.css('display', '') : ulTemplate);
                                        $.each(payload['errors'], function(key, value) {
                                            var liTemplate = $(ParsleyForm.options.errors.errorElem).addClass(key);
                                            $(ulError).append($(liTemplate).html(value));
                                        });

                                        $errorContainer.removeClass('hide');

                                        // enable the button again
                                        $form.find('input[name=submit]').prop('disabled', false);
                                        $form.find('input[type=submit]').prop('disabled', false);

                                    },
                                    success: function(data) {
                                        if (data['redirect']) {
                                            window.location.href = data['url'];
                                        } else if (data['modal']) {
                                            $form.closest('.modal').modal('hide');

                                            $(data['target']).modal({
                                                remote: data['url']
                                            });
                                        };
                                    }
                                });

                                return false;
                            };
                        } else {
                            var count = $errors.find('ul.parsley-error-list li').length;
                            if (count > 1) {
                                $errorContainer.find('p').html('There were ' + count + ' errors with this:');
                            } else if (count == 1) {
                                $errorContainer.find('p').html('There was 1 error with this:');
                            };

                            $errorContainer.removeClass('hide');

                            top = $form.offset().top;
                            $('html, body').animate({
                                scrollTop: top
                            }, ParsleyForm.options.scrollDuration);
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
