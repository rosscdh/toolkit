'use strict';
/*
Copyright (c) 2013 Ross Crawford-d'Heureuse.

2013. Updated by Ross Crawford-d'Heureuse <sendrossemail+imdb@gmail.com> to be a jquery.plugin
*/
$(function() {
    // the widget definition, where "custom" is the namespace,
    // "colorize" the widget name
    $.widget( "lawpal.elastic_search", {
        // default options
        key: undefined,
        search_by: undefined,

        display_template: undefined,

        options: {
            'uri': '/s/?q={search_param}',
            'display_template': undefined,                                      // - Must be an HTML template (**supports handlebarsjs.com)
            'callback': undefined,                                        // - Callback that can be called when the item is found
            'complete_callback': undefined,                                     // - Callback that can be called when the render is complete
            'delay': 500,
            'debug': true,
        },

        _log: function (msg) {
            var self = this;
            if (self.options.debug === true) {
                console.log(msg)
            }
        },
        // the constructor
        _create: function() {
            var self = this;

            self.options.callback = (self.options.callback !== undefined) ? self.options.callback : self.show ;

            self.display_template = (self.options.display_template) ? self.options.display_template : self.display_template;

            this._listen();
        },
        _listen: function () {
            var self = this;

            var delay = (function(){
              var timer = 0;
              return function(callback, ms){
                window.clearTimeout(timer);
                timer = window.setTimeout(callback, ms);
              };
            })();

            self.element.on('keyup', function (event) {
                window.clearTimeout();
                var query = self.element.val();

                if (query.length > 0) {
                    delay(function(){
                        self.query(query)
                    }, self.options.delay );
                }
            });
        },
        render_template: function () {
            var self = this;
            if ( typeof self.display_template == 'function' ) {
                return Handlebars.compile(self.display_template());
            } else {
                // is a string
                return Handlebars.compile(self.display_template);
            }
        },
        show: function (data, html, self) {
            self.element.append(html);
            console.log(data)
            console.log(html)
            if ( self.options.complete_callback ) {
                self.options.complete_callback(html, self);
            }
        },
        query: function (query) {
            var self = this;
            var template = self.render_template();
            var url = self.options.uri.assign({'search_param': query})

            self._log('Calling URI: {uri}'.assign({'uri': url}));

            $.ajax({
                type: 'GET',
                url: url,
                datatype: "jsonp",
                success: function(data, textStatus, jqXHR){
                    self._log('Success got a response: {data}'.assign({'data': data.length}))
                    var html = '';
                    $.each(data, function (i, context) {
                        html += template(context);
                    })

                    if ( self.options.callback ) {
                        self.options.callback(data, html, self);
                    }
                },

                error: function(data, textStatus, jqXHR){
                    self._log('There was an error')
                },

                complete: function() {
                    self._log('Completed Call')
                }
            }); // end ajax


        }
    });
});