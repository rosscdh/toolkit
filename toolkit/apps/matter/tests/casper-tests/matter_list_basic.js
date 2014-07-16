'use strict';
casper.test.comment(casper.cli.options.test_label);

var helper = require(casper.cli.options.casper_helper_js_path);

/**
*
*/
helper.scenario(casper.cli.options.url,
    function () {
        /* Basic page title test */
        this.test.assertHttpStatus(200);
        this.test.assertMatch(this.getTitle(), /^Your Matters/ig);

        // test search form
        // helper.capturePage()
        // casper.debugHTML()

    },
    /**
    * Test we ahve all apropriate controls present
    **/
    function () {
        //this.test.assertSelectorHasText('input[name="q"]', 'Search matters by name or client name...', "Matter list has a search input");
        //this.echo(casper.debugHTML());
        var num_matters = document.querySelectorAll('div#matter-list article.matter');

        this.test.assertExists('div#matter-list');
        this.test.assertExists('input');

        casper.waitFor(function check() {
            return this.evaluate(function() {
                return document.querySelectorAll('input[name=q]').length === 1;
            });
        }, function then() {
            helper.capturePage()
        });

        // --
    }
);

helper.run();