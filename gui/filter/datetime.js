/**
 * @class timeago
 * @classdesc                           Convert a date to n years/months/days/hours/minutes and seconds ago
 *
 * @example
 * &lt;div ng-bind="lastUpdated | timeago"&gt;&lt;/div&gt;
 *
 * @return {String} Reformatted text
 */
angular.module('toolkit-gui').filter('timeago', function () {
    return function (datestr) {
        if(!datestr) {
            return '';
        }

        var timeago = moment(datestr, "YYYY-MM-DDTHH:mm:ss.SSSZ").fromNow();

        return timeago;
    };
});

angular.module('toolkit-gui').filter('fromnow', function () {
    return function (datestr) {
        if(!datestr) {
            return '';
        }

        var fromnow = moment(datestr, "YYYY-MM-DDTHH:mm:ss.SSSZ").fromNow(true);

        return fromnow;
    };
});

angular.module('toolkit-gui').filter('duestatus', function () {
    return function (datestr) {
        if(!datestr) {
            return '';
        }

        var due_date = moment(datestr, "YYYY-MM-DDTHH:mm:ss.SSSZ");
        var curr_time = moment();

        if (curr_time.add(moment.duration(5, 'd')) > due_date){
            return 'btn-danger';
        } else {
            return 'btn-default';
        }
    };
});
