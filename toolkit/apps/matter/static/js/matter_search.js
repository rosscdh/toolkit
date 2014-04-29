/** @jsx React.DOM */
/**
* ReactJS Experiment
*
*/
var MatterItem = React.createClass({displayName: 'MatterItem',
  render: function() {
    return (
            React.DOM.article( {className:"col-md-4 matter"}, 
                React.DOM.div( {className:"card"}, 

                     this.props.editMatterInterface, 
                    
                    React.DOM.a( {href: this.props.detail_url,  title: this.props.name,  className:"content"}, 
                        React.DOM.div( {className:"title"}, 
                            React.DOM.h6(null,  this.props.lawyer_or_client_name ),
                            React.DOM.h5(null,  this.props.name )
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
        var userNodes = this.props.data.map(function (user) {
            //console.log(user)
            return (
                React.DOM.div( {className:"avatar img-circle"}, 
                    React.DOM.span( {className:"initials", title: user.name },  user.initials )
                )
            )
        });

        return (
          React.DOM.div( {className:"people pull-right"}, 
            userNodes
          )
        );
    }
});

var LatUpdatedOrComplete = React.createClass({displayName: 'LatUpdatedOrComplete',
    render: function() {
        var percent_complete = this.props.percent_complete;
        var date_modified = this.props.date_modified;
        var date_modified_ago = moment(date_modified).fromNow();

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
                React.DOM.a( {href:edit_url, 'data-toggle':"modal", 'data-target':modal_target, className:"edit"}, 
                    React.DOM.span( {className:"fui-gear"})
                )
            );

        } else {

            return '';
        }
    }
});


var NoResultsInterface = React.createClass({displayName: 'NoResultsInterface',
    render: function() {
        return (
            React.DOM.div(null, React.DOM.b(null, "Nothing found"))
        );
    },
});


var MatterList = React.createClass({displayName: 'MatterList',
  fuse: new Fuse(MatterListData, { keys: ["name", "matter_code", "client.name"], threshold: 0.35 }),
  getInitialState: function() {
    return {
        'matters': MatterListData,
        'total_num_matters': MatterListData.length
    }
  },
  handleChange: function(event) {
    var searchFor = event.target.value;
    var matter_list_results = (searchFor != '') ? this.fuse.search(event.target.value) : MatterListData
    this.setState({
        'matters': matter_list_results,
        'total_num_matters': matter_list_results.length
    });
  },
  render: function() {
    var matterNodes = null;

    if ( this.state.total_num_matters == 0 ) {

        matterNodes = NoResultsInterface(null )

    } else {
        matterNodes = this.state.matters.map(function (matter) {

            var editUrl = edit_url.replace('lp-react-name', matter.slug);
            var detailUrl = matter.base_url;

            var percentStyle = {'width': matter.percent_complete};
            var lawyer_or_client_name = (UserData.is_lawyer) ? (matter.client !== null) ? matter.client.name : null : matter.lawyer.name ;

            var participantList = Participants( {data:matter.participants} )
            var lastupdatedOrComplete = LatUpdatedOrComplete( {percent_complete:matter.percent_complete,
                                                              date_modified:matter.date_modified} )
            var editMatterInterface = EditMatterInterface( {key:matter.slug, can_edit:UserData.can_edit, edit_url:editUrl} )

            return MatterItem( 
                    {key:matter.slug,
                    name:matter.name,
                    is_lawyer:UserData.is_lawyer,
                    lawyer_or_client_name:lawyer_or_client_name,

                    participantList:participantList,
                    lastupdated_or_complete:lastupdatedOrComplete,
                    editMatterInterface:editMatterInterface,

                    percent_complete:matter.percent_complete,
                    percentStyle:percentStyle,
                    detail_url:detailUrl,
                    edit_url:editUrl}, matter)
        });
    }
    return (
      React.DOM.div(null, 
        React.DOM.form( {className:"form-horizontal", role:"form"}, 
            React.DOM.div( {className:"input-group"}, 
              React.DOM.input( {className:"input-lg", onChange:this.handleChange, autocomplete:"off", id:"id_q", name:"q", 'parsley-required':"true", 'parsley-required-message':"This field is required.", placeholder:"Search Matters", type:"text"} ),
              React.DOM.span( {className:"input-group-addon input-lg"}, React.DOM.b(null, this.state.total_num_matters))
            )
        ),
        React.DOM.br(null),
        matterNodes
      )
    );
  }
});

React.renderComponent(
  MatterList(null ),
  document.getElementById('matter-content')
);