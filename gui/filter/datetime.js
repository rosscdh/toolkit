/**
 * @class readabletimediff
 * @classdesc                           Convert a date to n years/months/days/hours/minutes and seconds ago
 *
 * @example
 * &lt;div ng-bind="lastUpdated | readabletimediff"&gt;&lt;/div&gt;
 *
 * @return {String} Reformatted text
 */
angular.module('toolkit-gui').filter('readabletimediff', function () {
    return function (datestr) {
        var diff, rv, yrs;

        if(!datestr) {
            return '';
        }

        datestr = datestr.substring(0,datestr.length-5);

        //datejs dateparser returns null; @lee: please check
        //var d1 = Date.now();
        //var d2 = Date.parseExact(datestr,"yyyy-MM-ddTHH:mm:ss");

        var d1 = new Date();
        var d2 = new Date(datestr);

        diff = new TimeSpan(d1 - d2);
        //console.log(diff);
        if (diff.days > 0) {
            // A day or more difference
            if (diff.days === 1) {
                rv = "yesterday";
            }
            else if (diff.days >= 365) {
                yrs = diff.days / 365;
                if (yrs === 1) {
                    rv = "1 year ago";
                }
                else {
                    rv = yrs + " years ago";
                }
            }
            else {
                rv = diff.days + " ago";
            }
        }
        else {
            // Less than 1 day difference
            if (diff.hours > 0) {
                if (diff.hours === 1) {
                    rv = "1 hour ago";
                }
                else {
                    rv = diff.hours + " hours ago";
                }
            }
            else if (diff.minutes > 0) {
                if (diff.minutes === 1) {
                    rv = "1 minute ago";
                }
                else {
                    rv = diff.minutes + " minutes ago";
                }
            }
            else {
                rv = "just now";
            }

            return rv;
        }

        return '';
    };
});