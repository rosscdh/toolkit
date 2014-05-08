/** @jsx React.DOM */
/**
* ReactJS Experiment
*
*/
var ExportButtonInterface = React.createClass({
    getInitialState: function() {
        return {
            'export_message': null,
            'export_message_classname': null
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
                // console.log(data)
                self.setState({
                    'export_message': data.detail,
                    'export_message_classname': 'palette-midnight-blue'
                });
            },
            error: function(result, a, b) {
                data = result.responseJSON
                self.setState({
                    'export_message': data.detail,
                    'export_message_classname': 'palette-pomegranate'
                });
            }.bind(this)
        });
    },
    render: function() {
        console.log(this.props.is_matter_owner)
        if (this.props.is_matter_owner === false) {
            // is not the owner (matter.lawyer)
            return (<span/>);
        }else{
            // is the matter owner
            return (
                <div>
                <button className="btn btn-inverse" onClick={this.handleClick}><span className="fui-check-inverted"></span> Export
                </button><span className="{this.state.export_message_classname}">{this.state.export_message}</span>
                </div>
            );
        };
    }
});

var MatterItem = React.createClass({
  render: function() {

    var ExportButton = <ExportButtonInterface is_matter_owner={this.props.is_matter_owner} matter_slug={this.props.key} />

    return (
            <article className="col-md-4 matter">
                <div className="card">

                    { this.props.editMatterInterface }
                    { ExportButton }

                    <a href={ this.props.detail_url } title={ this.props.name } className="content">
                        <div className="title">
                            <h6>{ this.props.lawyer_or_client_name }</h6>
                            <h5>{ this.props.name }</h5>
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

var LatUpdatedOrComplete = React.createClass({
    render: function() {
        var percent_complete = this.props.percent_complete;
        var date_modified = this.props.date_modified;
        var date_modified_ago = moment(date_modified).fromNow();

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
                <a href={edit_url} data-toggle="modal" data-target={modal_target} className="edit">
                    <span className="fui-gear"></span>
                </a>
            );

        } else {

            return '';
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

                var participantList = <Participants data={matter.participants} />
                var lastupdatedOrComplete = <LatUpdatedOrComplete percent_complete={matter.percent_complete}
                                                                  date_modified={matter.date_modified} />
                var editMatterInterface = <EditMatterInterface key={matter.slug} can_edit={UserData.can_edit} edit_url={editUrl} />

                var is_matter_owner = matter.lawyer.username == UserData.username

                return <MatterItem
                        key={matter.slug}
                        name={matter.name}
                        is_lawyer={UserData.is_lawyer}
                        is_matter_owner={is_matter_owner}
                        lawyer_or_client_name={lawyer_or_client_name}

                        participantList={participantList}
                        lastupdated_or_complete={lastupdatedOrComplete}
                        editMatterInterface={editMatterInterface}

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
