


angular.module('toolkit-gui').filter('fullname', function () {
    return function (participant) {
        if (participant != null) {
            if (participant.name != null) {
                return participant.name;
            } else if (participant.last_name != null && participant.last_name.length >0) {
                return participant.first_name + ' ' + participant.last_name;
            } else {
                return participant.email;
            }
        } else {
            return '';
        }
    };
});

angular.module('toolkit-gui').filter('initials', function () {
    return function (participant, showBracket) {
        if (participant != null) {
                 if (participant.initials != null && participant.initials.length>0) {
                     if (showBracket === true) {
                        return '(' + participant.initials + ')';
                     } else {
                        return participant.initials;
                     }
                 } else {
                     return '';
                 }
        } else {
            return '';
        }
    };
});
