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
        this.test.assertMatch(this.getTitle(), /^Lawpal \(test\) \- Lawpal$/ig);

        // test search form
        // helper.capturePage()
        // casper.debugHTML()

    },
    /**
    * Test basic layout is correct
    **/
    function () {
        //helper.capturePage()
        // test for nav
        this.test.assertExists('div.navbar.navbar-inverse.checklist-nav.ng-scope')
        // test for primary layout
        this.test.assertExists('div.container-fluid.full div.row.full')
        this.test.assertExists('div.container-fluid.full div.row.full div#checklist-items')

        this.test.assertExists('div.container-fluid.full div.row.full div#checklist-detail-container')
        this.test.assertExists('div.container-fluid.full div.row.full div#checklist-detail-container div#checklist-detail')
        this.test.assertExists('div.container-fluid.full div.row.full div#checklist-detail-container div#checklist-activity')
        
    },
    /**
    * Test we have all of the controls in the nav
    **/
    function () {
        helper.capturePage()
    },
    /**
    * Test we have the controls to add items
    **/
    function () {
        //helper.capturePage()
        this.test.assertExists('div.container-fluid.full div.row.full div#checklist-items h5')
        var h5_attribs = this.getElementInfo('div.container-fluid.full div.row.full div#checklist-items h5');

        casper.echo(JSON.stringify(h5_attribs), 'INFO')

        this.test.assertEquals(h5_attribs.text, 'UNCATEGORIZED')

    }
);

helper.run();