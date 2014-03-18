(function($) {
    $(function() {
        filepicker.setKey(window.GLOBALS['FILEPICKER_API_KEY']);

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
                        'X-CSRFToken': $('input[name=csrf_token]').val()
                    },
                    type: 'PATCH',
                    url: $elem.attr('data-remote'),
                    error: function(data) {
                        document.location.reload();
                    },
                    success: function(data) {
                        document.location.reload();
                    },
                    complete: function() {
                        document.location.reload();
                    }
                });
            });
        });
    });
})(jQuery);
