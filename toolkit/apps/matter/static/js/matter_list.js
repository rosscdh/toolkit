/** @jsx React.DOM */
/**
* ReactJS Experiment
*
*/
var DownloadExportView = React.createClass({displayName: 'DownloadExportView',
    render: function () {
        if ( this.props.download_url ) {
            return (
                React.DOM.span( {className:"download-link"}, 
                    React.DOM.a( {href:this.props.download_url}, "(Download)")
                )
            );
        } else {
            return (React.DOM.span(null));
        }
    }
});

var LastExportRequestedView = React.createClass({displayName: 'LastExportRequestedView',
    render: function () {
        var last_export_requested = moment(this.props.export_info.last_export_requested).from(moment.utc());
        var last_export_requested_by = this.props.export_info.last_export_requested_by;
        var download = DownloadExportView( {download_url:this.props.export_info.download_url})
        if (last_export_requested_by) {
            return (
                    React.DOM.span( {className:"export-message"}, 
                    React.DOM.p(null, React.DOM.b(null, "Last Requested:"), " ", last_export_requested,", ", last_export_requested_by, " ", download)
                    )
            );
        } else {
            return (React.DOM.span(null));
        }
    }
});

var ExportButtonInterface = React.createClass({displayName: 'ExportButtonInterface',
    getInitialState: function() {
        var is_pending_export = this.props.export_info.is_pending_export
        var requested_by = this.props.export_info.last_export_requested_by

        if (is_pending_export == true) {
            return {
                'show_export': false,
                'export_message': 'Export requested by ' + requested_by,
                'export_message_classname': null
            }
        } else {
            return {
                'show_export': true,
                'export_message': null,
                'export_message_classname': null
            }
        }
    },
    handleClick: function(event) {
        var self = this;
        var url = '/api/v1/matters/'+ this.props.matter_slug +'/export';

        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]:first').val()},
            success: function(data) {
                self.setState({
                    'show_export': false,
                    'export_message': data.detail,
                    'export_message_classname': 'palette-midnight-blue'
                });
            },
            error: function(result, a, b) {
                data = result.responseJSON
                self.setState({
                    'show_export': false,
                    'export_message': data.detail,
                    'export_message_classname': 'palette-pomegranate'
                });
            }.bind(this)
        });
    },
    render: function() {
        if (this.props.is_matter_lawyer_participant === false) {
            // is not the owner (matter.lawyer)
            return (React.DOM.div( {className:"btn btn-sm btn-link"} ));
        }else{
            // is the matter owner
            var className = (this.state.show_export === true)? 'btn btn-sm btn-link export-button' : 'btn btn-sm btn-default disabled dis-export-button';
            var export_message = this.state.export_message;
            //var LastExported = <LastExportedView export_info={this.props.export_info}/>
            var LastExportRequested = LastExportRequestedView( {export_info:this.props.export_info})
            return (
                React.DOM.div(null, 
                React.DOM.button( {className:className, 'data-toggle':"tooltip", 'data-placement':"left", title:"Export this Matter", onClick:this.handleClick}, React.DOM.span( {className:"fui-exit"})
                ),React.DOM.span( {className:"export-message"}, React.DOM.p(null, React.DOM.i(null, export_message))),React.DOM.br(null),LastExportRequested
                )
            );
        };
    }
});

var MatterItem = React.createClass({displayName: 'MatterItem',
  render: function() {

    var ExportButton = ExportButtonInterface( {is_matter_lawyer_participant:this.props.is_matter_lawyer_participant, matter_slug:this.props.key, export_info:this.props.export_info} )

    return (
            React.DOM.article( {className:"col-md-4 matter"}, 
                React.DOM.div( {className:"card"}, 

                     this.props.editMatterInterface, 
                     ExportButton, 

                    React.DOM.a( {href: this.props.detail_url,  title: this.props.name,  className:"content"}, 
                        React.DOM.div( {className:"title"}, 
                            React.DOM.h6(null,  this.props.lawyer_or_client_name ),
                            React.DOM.h5(null,  this.props.name ),
                             this.props.currentUserRole 
                        ),
                        React.DOM.div( {className:"meta clearfix"}, 
                             this.props.lastupdated_or_complete, 
                             this.props.participantList 
                        )
                    ),
                    React.DOM.div( {className:"progress"}, 
                        React.DOM.div( {className:"progress-bar", style: this.props.percentStyle })
                    )
                )
            )
    );
  }
});

var Participants = React.createClass({displayName: 'Participants',
    render: function() {
        if (this.props.data.length > 3) {
            var userNames = this.props.data.map(function(user) {
                return user.name;
            });

            return (
                React.DOM.div( {className:"people people-multi pull-right", 'data-toggle':"tooltip", title:userNames}, 
                    React.DOM.div( {className:"avatar img-circle one"}, 
                        React.DOM.span( {className:"initials"}, this.props.data.length)
                    ),
                    React.DOM.div( {className:"avatar img-circle two"}, React.DOM.span( {className:"initials"}, " ")),
                    React.DOM.div( {className:"avatar img-circle three"}, React.DOM.span( {className:"initials"}, " "))
                )
            );
        } else {
            var userNodes = this.props.data.map(function(user) {
                return (
                    React.DOM.div( {className:"avatar img-circle"}, 
                        React.DOM.span( {className:"initials", title:user.name}, user.initials)
                    )
                )
            });

            return (
                React.DOM.div( {className:"people pull-right"}, 
                    userNodes
                )
            );
        }
    }
});

var CurrentUserRole = React.createClass({displayName: 'CurrentUserRole',
    render: function() {

        var role = null;
        for (var i = 0; i < this.props.data.length; i++) {
            if (this.props.data[i].username == UserData.username) {
                role = this.props.data[i].role;
            }
        }


        if (role === 'owner') {
            return (

                React.DOM.span( {className:"fui-star-2", 'data-toggle':"tooltip", 'data-placement':"right", title:"You are the Matter Owner"})
                );
        }
        else {
            return (
                React.DOM.div(null)
                );
        }

    }
});

var LastUpdatedOrComplete = React.createClass({displayName: 'LastUpdatedOrComplete',
    render: function() {
        var percent_complete = this.props.percent_complete;
        var date_modified = this.props.date_modified;
        var date_modified_ago = moment(date_modified).from(moment.utc());

        if (percent_complete === '100%') {

            return (
                React.DOM.p( {className:"small pull-left done"}, React.DOM.span( {className:"fui-check-inverted"}), " Complete")
            );

        } else {

            return (
                React.DOM.p( {className:"small pull-left"}, "Last updated ", React.DOM.time( {datetime: date_modified },  date_modified_ago ))
            );
        }
    }
});


var EditMatterInterface = React.createClass({displayName: 'EditMatterInterface',
    render: function() {
        var key = this.props.key;
        var can_edit = this.props.can_edit;
        var edit_url = this.props.edit_url;
        var modal_target = '#matter-edit-' + key;
        if (can_edit === true) {

            return (
                React.DOM.a( {href:edit_url, 'data-toggle':"modal", 'data-target':modal_target, className:"edit btn-sm"}, 
                    React.DOM.span( {className:"fui-gear", 'data-toggle':"tooltip", 'data-placement':"left", title:"Edit Matter Details"})
                )
            );

        } else {

            return (React.DOM.span(null));
        }
    }
});


var NoResultsInterface = React.createClass({displayName: 'NoResultsInterface',
    render: function() {
        return (
            React.DOM.div( {className:"col-md-12 text-center"}, 
                React.DOM.h6( {className:"text-muted"}, "Could not find any matters.")
            )
        );
    },
});


var CreateMatterButton = React.createClass({displayName: 'CreateMatterButton',
    render: function() {
        var create_url = this.props.create_url;
        return (
            React.DOM.a( {href:create_url, 'data-toggle':"modal", 'data-target':"#matter-create", className:"btn btn-success btn-embossed pull-right"}, React.DOM.i( {className:"fui-plus"}), " New Matter")
        );
    },
});


var MatterList = React.createClass({displayName: 'MatterList',
    fuse: new Fuse(MatterListData, { keys: ["name", "matter_code", "client.name"], threshold: 0.35 }),
    getInitialState: function() {
        return {
            'can_create': UserData.can_create,
            'matters': MatterListData,
            'total_num_matters': MatterListData.length
        }
    },
    handleSearch: function(event) {
        var searchFor = event.target.value;
        var matter_list_results = (searchFor != '') ? this.fuse.search(event.target.value) : MatterListData

        this.setState({
            matters: matter_list_results,
            total_num_matters: matter_list_results.length,
            searched: true
        });
    },
    render: function() {
        var matterNodes = null;

        var createButton = null;
        if (this.state.can_create) {
            createButton = CreateMatterButton( {create_url:create_url})
        }

        if ( this.state.total_num_matters == 0 ) {
            matterNodes = NoResultsInterface(null )
        } else {
            matterNodes = this.state.matters.map(function (matter) {
                var editUrl = edit_url.replace('lp-react-name', matter.slug);
                var detailUrl = matter.base_url;

                var percentStyle = {'width': matter.percent_complete};
                var lawyer_or_client_name = (UserData.is_lawyer) ? (matter.client !== null) ? matter.client.name : null : matter.lawyer.name ;

                var currentUserRole = CurrentUserRole( {data:matter.participants} )
                var participantList = Participants( {data:matter.participants} )
                var lastupdatedOrComplete = LastUpdatedOrComplete( {percent_complete:matter.percent_complete,
                                                                  date_modified:matter.date_modified} )
                var editMatterInterface = EditMatterInterface( {key:matter.slug, can_edit:UserData.can_edit, edit_url:editUrl} )

                var is_matter_lawyer_participant = UserData.is_lawyer;

                return MatterItem(
                        {key:matter.slug,
                        name:matter.name,
                        is_lawyer:UserData.is_lawyer,
                        is_matter_lawyer_participant:is_matter_lawyer_participant,
                        lawyer_or_client_name:lawyer_or_client_name,
                        currentUserRole:currentUserRole,
                        participantList:participantList,
                        lastupdated_or_complete:lastupdatedOrComplete,
                        editMatterInterface:editMatterInterface,

                        export_info:matter.export_info,

                        percent_complete:matter.percent_complete,
                        percentStyle:percentStyle,
                        detail_url:detailUrl,
                        edit_url:editUrl}, matter)
            });
        }
        return (
            React.DOM.section( {className:"matters cards"}, 
                React.DOM.header( {className:"page-header"}, 
                    React.DOM.h4(null, "All Matters"),
                    React.DOM.div( {className:"pull-right"}, 
                        createButton,
                        React.DOM.div( {className:"form-group pull-right"}, 
                            React.DOM.div( {className:"input-group search-field"}, 
                                React.DOM.input( {type:"text", className:"form-control", placeholder:"Search matters by name or client name...", name:"q", autocomplete:"off", onChange:this.handleSearch}),
                                React.DOM.span( {className:"input-group-btn"}, 
                                    React.DOM.button( {type:"submit", className:"btn"}, React.DOM.span( {className:"fui-search"}))
                                )
                            )
                        )
                    )
                ),
                React.DOM.div( {className:"row"}, 
                    matterNodes
                )
            )
        );
    }
});

React.renderComponent(
  MatterList(null ),
  document.getElementById('matter-list')
);
