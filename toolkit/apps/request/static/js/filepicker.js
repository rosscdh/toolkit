(function($) {
    $(function() {
        filepicker.setKey(window.GLOBALS['FILEPICKER_API_KEY']);

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        $(document).on('click.filepicker.data-api', '[data-toggle=filepicker]', function() {
            var $elem = $(this);

            filepicker.pickAndStore({
                'container': 'modal',
                'services': ['BOX','COMPUTER','DROPBOX','EVERNOTE','FTP','GITHUB','GOOGLE_DRIVE','SKYDRIVE','WEBDAV']
            }, {
                'location': 'S3',
                'path': '/uploads/'
            }, function(files) {
                $.ajax({
                    data: JSON.stringify({
                        name: files[0].filename,
                        executed_file: files[0].url
                    }),
                    dataType: 'json',
                    headers: {
                        'Accept' : 'application/json',
                        'Content-Type' : 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    type: 'POST',
                    url: $elem.attr('data-remote'),
                    error: function(data) {
                        //document.location.reload();
                    },
                    success: function(data) {
                        document.location.reload();
                    },
                    complete: function() {
                        //document.location.reload();
                    }
                });
            });
        });
    });
})(jQuery);
