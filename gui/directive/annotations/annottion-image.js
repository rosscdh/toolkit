/**
 * Author: Lee Sinclair
 */
angular.module('image.annotation', [])
.directive("annotateImage", [ '$timeout', function($timeout){
	'use strict';
	return {
		'scope': {
			'callback': '&callback',
			'replycallback': '&replycallback',
			'annotations': '=annotations',
			'name': '=name'
		},
		'transclude': true,
		'restrict': 'A',
		'templateUrl': 'imageAnnotation.html',
		'link': function(scope, element/*, attrs*/) {
			var el = $(element);

			var parentWidth = el.width();
			var parentHeight = el.height();

			scope.jAnnotations = $(element);
			scope.jAnnotations.css('position','relative');

			//scope.annotations = [];
			scope.adata = {
				'selected': null,
				'editing': false,
				'reply': '',
				'dim': {
					'width': parentWidth,
					'height': parentHeight
				}
			};

			/**
			 * selectPosition
			 * @param  {Event} e Click event (probably)
			 */
			scope.selectPosition = function(e){
				e.preventDefault();

				// Check if leaving a text field
				if(!scope.adata.editing) {
					var parent = $(e.target).parent();
					var parentOffset = parent.offset();

					//or $(this).offset(); if you really just want the current element's offset
					var relX = (e.pageX - parentOffset.left -20) / parentWidth;
					var relY = (e.pageY - parentOffset.top -40) / parentHeight;

					var pos = {
						'x': relX,
						'y': relY
					};

					var annotation = {
						'question': '',
						'position': pos,
						'show': true,
						'replies': []
					};

					scope.annotations =  scope.annotations || [];
					scope.annotations.push( annotation );
					scope.startEditing( annotation, scope.annotations.length-1 );
				}
			};

			scope.startEditing = function( annotation, idx ) {
				scope.adata.editing = true;
				scope.adata.selected = idx;
			};

			scope.stopEditing = function(annotation,idx) {
				if(annotation.question==='') {
					scope.remove(idx);
				}

				$timeout( function(){
					scope.adata.editing = false;
				},600);

				scope.adata.selected = -1;
			};

			scope.processKeyPress = function(e, annotation) {
				if (e.which===13) {
					scope.adata.editing = false;
					scope.callback( { 'annotation': annotation } );
				}
			};
			
			scope.updateAnnotation = function(annotation) {
				if (annotation.question!=='') {
					scope.adata.editing = false;
					scope.callback( { 'annotation': annotation } );
				}
			};

			scope.addReply = function( e, annotation, reply ) {
				if (e.which===13) {
					annotation.replies = annotation.replies || [];
					var replyData = { 'user': scope.name, 'text': reply, 'at': new Date() };
					annotation.replies.push( replyData );
					scope.replycallback( { 'annotation': annotation, 'reply': replyData } );
					scope.adata.reply = '';
				}
			};

			scope.remove =function(idx){
				scope.annotations.splice(idx,1);
			};

			scope.stop = function(e) {
				e.stopPropagation();
			};
		}
	};
}]).directive('initFocus', function() {
	'use strict';
    var timer;
    
    return function(scope, elm/*, attr*/) {
        if (timer) {
        	clearTimeout(timer);
        }
        
        timer = setTimeout(function() {
            elm.focus();
            console.log('focus', elm);
        }, 600);
    };
});

angular.module('image.annotation').run(['$templateCache', function($templateCache) {
	'use strict';
	$templateCache.put('imageAnnotation.html',
		'<div ng-click="selectPosition($event)">\n' +
		'  <div ng-transclude></div>\n'+
		'  <div class="annotation" ng-repeat="annotation in annotations" ng-style="{\'position\':\'absolute\', \'left\': (annotation.position.x * adata.dim.width) + \'px\', \'top\': (annotation.position.y * adata.dim.height) +\'px\'}" ng-class="{\'focus\':annotation.show||adata.selected===$index}" ng-click="stop($event)" ng-mouseEnter="annotation.show=true"  ng-mouseLeave="annotation.show=false">\n'+
		'    <i class="glyphicon glyphicon-comment pointer">&nbsp;</i>\n'+
		'    <button class="btn btn-link text-danger" ng-click="updateAnnotation(annotation);stop($event)"><i class="glyphicon glyphicon-ok"></i></button>\n'+
		'    <input type="text" placeholder="Question/Comment" ng-click="stop($event)" ng-keypress="processKeyPress($event, annotation)" ng-model="annotation.question" ng-show="adata.editing" ng-focus="startEditing(annotation, $index)" ng-blur="stopEditing(annotation,$index)" init-focus />\n'+
		'    <blockquote ng-bind="annotation.question" ng-show="!adata.editing" ng-click="startEditing(annotation,$index)"></blockquote>\n'+
		'    <div ng-repeat="reply in annotation.replies" class="reply clearfix">\n'+
		'       <p ng-bind="reply.text" class="clearfix"></p>\n'+
		'       <p class="clearfix text-muted"><small><i class="glyphicon glyphicon-user pull-left"></i>\n'+
		'         <em ng-bind="reply.user" class="from pull-left"></em>\n'+
		'         <em ng-bind="reply.at | date:\'short\' " class="date pull-right"></em>\n'+
		'       </small></p>\n'+
		'    </div>\n'+
		'    <input type="text" ng-model="adata.reply" ng-keypress="addReply($event, annotation, adata.reply)" ng-show="adata.editing!==true" placeholder="Add a reply" style="margin-top:0.3em;" />\n'+
		'  </div>\n'+
		'</div>\n' +
		'');
}]);