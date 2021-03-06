/** @jsx React.DOM */
/**
* ReactJS Experiment
*
*/
var DownloadExportView = React.createClass({
    render: function () {
        if ( this.props.download_url ) {
            return (
                <span className='download-link'>
                    <a href={this.props.download_url}>(Download)</a>
                </span>
            );
        } else {
            return (<span/>);
        }
    }
});

var FlashMessageView = React.createClass({
    getInitialState: function() {
        return {
                'message': null,
        }
    },
    handleFlashMessage: function (event) {
        console.log(event)
        this.setState({
            'message': event.message
        });
    },
    componentDidMount: function() {
        var self = this;
        $( "body" ).on( "alert_message", function( event ) {
            self.handleFlashMessage( event );
        });
    },
    render: function () {
        blockClassName = (this.state.message !== null) ? 'alert alert-warning fade in' : 'hide' ;
        return (
            <div className={blockClassName} role="alert">
                {this.state.message}
            </div>
        );
    }
});

var LastExportRequestedView = React.createClass({
    render: function () {
        var last_export_requested = moment(this.props.export_info.last_export_requested).from(moment.utc());
        var last_export_requested_by = this.props.export_info.last_export_requested_by;
        var download = <DownloadExportView download_url={this.props.export_info.download_url}/>
        if (last_export_requested_by) {
            return (
                    <span className="export-message">
                    <p><b>Last Requested:</b> {last_export_requested}, {last_export_requested_by} {download}</p>
                    </span>
            );
        } else {
            return (<span/>);
        }
    }
});

var ExportProvidersInterface = React.createClass({
    getInitialState: function() {
        return {
                'show_export': true,
                'export_message': null,
                'export_message_classname': null
        }
    },
    handleClick: function(provider, event) {
        var self = this;
        var url = '/api/v1/matters/'+ this.props.matter_slug +'/export';
        // append the provider to the url in the form
        // '/api/v1/matters/:slug/export/:provider';
        if ( provider !== 'default' ) {
            url += '/' + provider;
        }

        self.setState({
            'show_export': false,
            'export_message': 'Please wait... Exporting',
            'export_message_classname': 'palette-pomegranate'
        });
        //console.log(url)
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]:first').val()},
            success: function(data) {
                self.setState({
                    'export_message': data.detail,
                });
            },
            error: function(result, a, b) {
                data = result.responseJSON
                self.setState({
                    'export_message': data.detail,
                });
            }.bind(this)
        });
    },
    provider_name: function ( provider ) {
        if ( provider == 'box' ) {
            return 'Box.com';
        }
        if ( provider == 'dropbox-oauth2' ) {
            return 'Dropbox.com';
        }
        return 'Export as Zip'
    },
    // provider_logo: function ( provider ) {
    //     if ( provider == 'box' ) {
    //         return 'images/box/box-96x96.png';
    //     }
    //     if ( provider == 'dropbox-oauth2' ) {
    //         return 'images/dropbox/dropbox-logos_dropbox-vertical-blue.png';
    //     }
    //     return 'Export as Zip'
    // },
    render: function() {
        var self = this;
        var providers = {
            'default': <li><a ref="export_data" className="btn" title="Export this Matter" onClick={this.handleClick.bind(null, 'default')}><span className="fui-exit"></span>Export as Zip</a></li>,
        };
        this.props.integrations.forEach(function (r) {
            var provider_name = self.provider_name( r );
            var name = 'Export to ' + provider_name;
            var title = 'Export this Matter to ' + provider_name;
            providers[r] = <li><a ref="export_data" className="btn" title={title} onClick={self.handleClick.bind(null, r)}><span className="fui-exit"></span>{name}</a></li>;
        });

        var modalId = 'export-providers-'+ this.props.matter_slug;
        var modalTitle = 'Export of: ' + this.props.matter_name;
        var providerClass = (this.state.show_export === true) ? 'list-unstyled' : 'hide' ;

        if (this.state.export_message !== null) {
            var e = $.Event( "alert_message", { message: this.state.export_message, show_export: this.state.show_export } );
            $( "body" ).trigger( e );
        }

        return (
            <div className="modal" id={modalId}>
              <div className="modal-dialog">
                <div className="modal-content">
                  <div className="modal-header">
                    <button type="button" className="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span className="sr-only">Close</span></button>
                    <h4 className="modal-title">{modalTitle}</h4>
                  </div>
                  <div className="modal-body">
                    <span className={this.state.export_message_classname}>{this.state.export_message}</span>
                    <ul className={providerClass}>{providers}</ul>
                  </div>
                  <div className="modal-footer">
                    <button type="button" className="btn btn-default" data-dismiss="modal">Close</button>
                  </div>
                </div>
              </div>
            </div>
        );
    }
});

var ExportButtonView = React.createClass({
    getInitialState: function() {
        return {
            'integrations': UserData.integrations,
            'export_message': null,
            'show_export': true,
        }
    },
    handleClick: function(event) {
        var self = this;
        var url = '/api/v1/matters/'+ this.props.matter_slug +'/export';

        self.setState({
            'show_export': false,
            'export_message': 'Please wait... Exporting',
            'export_message_classname': 'palette-midnight-blue'
        });

        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]:first').val()},
            success: function(data) {
                self.setState({
                    'export_message': data.detail,
                });
            },
            error: function(result, a, b) {
                data = result.responseJSON
                self.setState({
                    'export_message': data.detail,
                });
            }.bind(this)
        });
    },
    render: function () {
        var className = (this.state.show_export === true) ? this.props.class_name : 'hide' ;

        if (this.state.export_message !== null) {
            var e = $.Event( "alert_message", { message: this.state.export_message, show_export: this.state.show_export } );
            $( "body" ).trigger( e );
        }

        if ( this.state.integrations.length == 0) {
            return (
                <button className={className} data-toggle="tooltip" data-placement="left" title="Export this Matter" onClick={this.handleClick}><span className="fui-exit"></span></button>
            )
        } else {
            var ExportProvidersModal = <ExportProvidersInterface
                                            matter_name={this.props.matter_name}
                                            matter_slug={this.props.matter_slug}
                                            integrations={this.state.integrations} />
            var modalId = '#export-providers-' + this.props.matter_slug;
            return (
                <div>
                <a href="" className={className} data-toggle="modal" data-target={modalId} title="Export this Matter from one of the available providers"><span className="fui-exit"></span></a>
                {ExportProvidersModal}</div>
            )
        }
    }
});


var ExportButtonInterface = React.createClass({
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

    render: function() {
        if (this.props.is_matter_lawyer_participant === false) {
            // is not the owner (matter.lawyer)
            return (<div className="btn btn-sm btn-link" />);
        }else{
            // is the matter owner
            var className = (this.state.show_export === true)? 'btn btn-sm btn-link export-button' : 'btn btn-sm btn-default disabled dis-export-button';
            var export_message = this.state.export_message;
            var LastExportRequested = <LastExportRequestedView
                                            export_info={this.props.export_info}/>

            var ExportButton = <ExportButtonView
                                    matter_name={this.props.matter_name}
                                    matter_slug={this.props.matter_slug}
                                    class_name={className} />
            return (
                <div>
                {ExportButton}<span className="export-message"><p><i>{export_message}</i></p></span><br/>{LastExportRequested}
                </div>
            );
        };
    }
});

var MatterItem = React.createClass({
  render: function() {

    var ExportButton = <ExportButtonInterface
                                is_matter_lawyer_participant={this.props.is_matter_lawyer_participant}
                                matter_slug={this.props.key}
                                matter_name={this.props.name}
                                export_info={this.props.export_info} />

    return (
            <article className="col-md-4 matter">
                <div className="card">

                    { this.props.editMatterInterface }
                    { ExportButton }

                    <a href={ this.props.detail_url } title={ this.props.name } className="content">
                        <div className="title">
                            <h6>{ this.props.lawyer_or_client_name }</h6>
                            <h5>{ this.props.name }</h5>
                            { this.props.currentUserRole }
                        </div>
                        <div className="meta clearfix">
                            { this.props.lastupdated_or_complete }
                            { this.props.participantList }
                        </div>
                    </a>
                    <div className="progress">
                        <div className="progress-bar" style={ this.props.percentStyle }></div>
                    </div>
                </div>
            </article>
    );
  }
});

var Participants = React.createClass({
    render: function() {
        if (this.props.data.length > 3) {
            var userNames = this.props.data.map(function(user) {
                return user.name;
            });

            return (
                <div className="people people-multi pull-right" data-toggle="tooltip" title={userNames}>
                    <div className="avatar img-circle one">
                        <span className="initials">{this.props.data.length}</span>
                    </div>
                    <div className="avatar img-circle two"><span className="initials">&nbsp;</span></div>
                    <div className="avatar img-circle three"><span className="initials">&nbsp;</span></div>
                </div>
            );
        } else {
            var userNodes = this.props.data.map(function(user) {
                return (
                    <div className="avatar img-circle">
                        <span className="initials" title={user.name}>{user.initials}</span>
                    </div>
                )
            });

            return (
                <div className="people pull-right">
                    {userNodes}
                </div>
            );
        }
    }
});

var CurrentUserRole = React.createClass({
    render: function() {

        var role = null;
        for (var i = 0; i < this.props.data.length; i++) {
            if (this.props.data[i].username == UserData.username) {
                role = this.props.data[i].role;
            }
        }


        if (role === 'owner') {
            return (
                <span className="fui-star-2" data-toggle="tooltip" data-placement="right" title="You are the Matter Owner"></span>
                );
        } else {
            return (
                <div />
                );
        }

    }
});

var LastUpdatedOrComplete = React.createClass({
    render: function() {
        var percent_complete = this.props.percent_complete;
        var date_modified = this.props.date_modified;
        var date_modified_ago = moment(date_modified).from(moment.utc());

        if (percent_complete === '100%') {

            return (
                <p className="small pull-left done"><span className="fui-check-inverted"></span> Complete</p>
            );

        } else {

            return (
                <p className="small pull-left">Last updated <time datetime={ date_modified }>{ date_modified_ago }</time></p>
            );
        }
    }
});


var EditMatterInterface = React.createClass({
    render: function() {
        var key = this.props.key;
        var can_edit = this.props.can_edit;
        var edit_url = this.props.edit_url;
        var modal_target = '#matter-edit-' + key;
        if (can_edit === true) {

            return (
                <a href={edit_url} data-toggle="modal" data-target={modal_target} className="edit btn-sm">
                    <span className="fui-gear" data-toggle="tooltip" data-placement="left" title="Edit Matter Details"></span>
                </a>
            );

        } else {

            return (<span/>);
        }
    }
});


var NoResultsInterface = React.createClass({
    render: function() {
        return (
            <div className="col-md-12 text-center">
                <h6 className="text-muted">Could not find any matters.</h6>
            </div>
        );
    },
});


var CreateMatterButton = React.createClass({
    render: function() {
        var create_url = this.props.create_url;
        return (
            <a href={create_url} data-toggle="modal" data-target="#matter-create" className="btn btn-success btn-embossed pull-right"><i className="fui-plus"></i> New Matter</a>
        );
    },
});


var MatterList = React.createClass({
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
        var flashMessage = <FlashMessageView />
        var createButton = null;
        if (this.state.can_create) {
            createButton = <CreateMatterButton create_url={create_url}/>
        }

        if ( this.state.total_num_matters == 0 ) {
            matterNodes = <NoResultsInterface />
        } else {
            matterNodes = this.state.matters.map(function (matter) {
                var editUrl = edit_url.replace('lp-react-name', matter.slug);
                var detailUrl = matter.base_url;

                var percentStyle = {'width': matter.percent_complete};
                var lawyer_or_client_name = (UserData.is_lawyer) ? (matter.client !== null) ? matter.client.name : null : matter.lawyer.name ;

                var currentUserRole = <CurrentUserRole data={matter.participants} />
                var participantList = <Participants data={matter.participants} />
                var lastupdatedOrComplete = <LastUpdatedOrComplete percent_complete={matter.percent_complete}
                                                                  date_modified={matter.date_modified} />
                var editMatterInterface = <EditMatterInterface key={matter.slug} can_edit={UserData.can_edit} edit_url={editUrl} />

                var is_matter_lawyer_participant = UserData.is_lawyer;

                return <MatterItem
                        key={matter.slug}
                        name={matter.name}
                        is_lawyer={UserData.is_lawyer}
                        is_matter_lawyer_participant={is_matter_lawyer_participant}
                        lawyer_or_client_name={lawyer_or_client_name}
                        currentUserRole={currentUserRole}
                        participantList={participantList}
                        lastupdated_or_complete={lastupdatedOrComplete}
                        editMatterInterface={editMatterInterface}

                        export_info={matter.export_info}

                        percent_complete={matter.percent_complete}
                        percentStyle={percentStyle}
                        detail_url={detailUrl}
                        edit_url={editUrl}>{matter}</MatterItem>
            });
        }
        return (
            <section className="matters cards">
                <header className="page-header">
                    <h4>All Matters</h4>
                    <div className="pull-right">
                        {createButton}
                        <div className="form-group pull-right">
                            <div className="input-group search-field">
                                <input type="text" className="form-control" placeholder="Search matters by name or client name..." name="q" autocomplete="off" onChange={this.handleSearch}/>
                                <span className="input-group-btn">
                                    <button type="submit" className="btn"><span className="fui-search"></span></button>
                                </span>
                            </div>
                        </div>
                    </div>
                </header>
                <div className="row">
                    {flashMessage}
                    {matterNodes}
                </div>
            </section>
        );
    }
});

React.renderComponent(
  <MatterList />,
  document.getElementById('matter-list')
);
