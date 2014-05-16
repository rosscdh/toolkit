# Checklist GUI

The checklist GUI is a project designed to use the toolkit API to allow lawyers work with thier clients more effectively.

## Instructions
### 1. Install Node.js

Skip this section if you have a node evironment setup.

#### OS X

##### Prerequisites

This guides assumes you have installed the following tools successfully:
- git
- Homebrew

Use nave (or similar) to manage your Node.js installations. You should always try
to use the latest stable version of Node.js.

In a terminal, run:

	brew install node
	wget -qO- https://raw.github.com/creationix/nvm/master/install.sh | sh
	nvm use 0.10

If you have trouble getting node to link with nvm, check out:
  http://stackoverflow.com/questions/12607155/error-the-brew-link-step-did-not-complete-successfully





Then each time you open a terminal:

	nvm use 0.10

### 2. Install development tools

	npm install -g bower grunt-cli yo generator-cg-angular

- `bower` installs and manages many client-side dependencies (e.g. jQuery)
- `grunt-cli` used to execute grunt tasks defined in the project
- `yo` and `generator-static` will install yeoman and this generator
- `generator-cg-angular` scaffhold angular partials, filters and services

### 3. Update the project

Let's update the project modules:

	cd gui
	bower install
	npm install

[generator-cg-angular](https://github.com/cgross/generator-cg-angular)

### 4. Preconfigured libraries

The new app will have a handful of preconfigured libraries included.

* This includes Angular 1.2,
* Bootstrap 3,
* AngularUI Bootstrap,
* AngularUI Utils,
* FontAwesome 4,
* JQuery 2,
* Underscore 1.5,
* LESS 1.5, and
* Moment 2.5.

### 4. Subgenerators

There are a set of sub-generators to initialize empty Angular components.  Each of these generators will:

* Create one or more skeleton files (javascript, LESS, html, spec etc) for the component type.
* Update index.html and add the necessary `script` tags.
* Update app.less and add the @import as needed.
* For partials, update the setup.js, adding the necessary route call if a route was entered in the generator prompts.

There are generators for `directive`,`partial`,`service`, and `filter`.

Running a generator:

    yo cg-angular:directive my-awesome-directive
    yo cg-angular:partial my-partial
    yo cg-angular:service my-service
    yo cg-angular:filter my-filter

### 5. Build/Debug

The build process generates a gui/dist folder with with compressed css and js.

Grunt is used as the task runner. To build the your code run:

	grunt build

Grunt can runs the Angular tests

	grunt test
