$(document).ready(function () {
    'use strict';

    var search_element = $('#search-q');

    search_element.on('blur', function (event) {
        search_element.popover('destroy');
    });

    search_element.elastic_search({
        delay: 600,
        display_template: function () {
            return '<a href="{{ url }}" class="list-group-item">' +
                '<span class="badge">{{ result_type }}</span>' +
                '<h6 class="list-group-item-heading">{{ name }}</h6>' +
                '{{#if description}}<p class="list-group-item-text">{{ description }}</p>{{/if}}' +
            '</a>';
        },
        callback: function (data, html, self) {

            html = '<div class="list-group">'+ html +'</div>'
            search_element.popover('destroy');

            if (data.length > 0) {

                search_element.popover({
                    placement: 'bottom',
                    trigger: 'manual',
                    title: 'Search results...',
                    html: true,
                    content: html
                });
                search_element.popover('show');

            } else {
                search_element.popover('destroy');
            }
        }
    });
});