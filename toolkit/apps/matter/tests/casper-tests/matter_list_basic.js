casper.test.comment(casper.cli.options.test_label);

var helper = require(casper.cli.options.casper_helper_js_path);

/**
*
*/
helper.scenario(casper.cli.options.url,
    function() {
        /* Basic page title test */
        this.test.assertHttpStatus(200);
        this.test.assertMatch(this.getTitle(), /^Your Matters/ig);

        // test search form
        helper.capturePage()
        casper.debugHTML()
        this.test.assertExists('input#id_q')

        // --
    }
);

helper.run();