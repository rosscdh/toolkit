(function($) {
  $(function() {

    // Summernote
    $("[data-toggle=summernote]").summernote({
      height: 200,
      toolbar: [
        ['style', ['bold', 'italic', 'underline', 'clear']],
        ['list', ['ul', 'ol']],
        ['para', ['paragraph']],
        ['fullscreen', ['fullscreen']]
      ],
      onblur: function() {
        var $this = $(this);
        var $el = $this.parent().siblings('[data-toggle=summernote]');

        $el.html($this.code());
      }
    });

  });
})(jQuery);
