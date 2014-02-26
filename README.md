LawPal - Toolkit
================

Toolkit is a simplified interface for adding tools and users to a generic
workspace.


Getting started
---------------

1. mkvirtualenv toolkit
2. pip install -r requirements/dev.txt
3. fab rebuild_local
4. honcho start


Pandoc
------

__Installing__

1. Mac: https://code.google.com/p/pandoc/downloads/detail?name=pandoc-1.12.3.pkg.zip&can=2&q= install the osx package
2. Ubuntu: apt-get install pandoc should do it

__PDF Latext__

In order to use the pandoc conversion of html to pdf you need to install latex

1. Mac: http://tug.org/mactex/
2. Ubuntu: http://java.dzone.com/articles/installing-latex-ubuntu


Testing
-------

### CasperJS && PhantomJS ###

__currently we dont use phantom but once angularjs arrives this will change__

__OSX__

Should be >= casperjs: 1.1.0-DEV
Should be >= phantomjs: 1.9.0

1. ```brew update```
2. ```brew install phantomjs```
2. ```brew install casperjs --devel```


__UBUNTU__

1. ```sudo apt-get install libxml2-dev libxslt1-dev```
