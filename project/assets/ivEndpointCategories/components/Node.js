import _ from 'underscore';
import React from 'react';

import EditNode from './EditNode';


class Node extends React.Component {

    constructor() {
        super();
        this.state = {
            showForm: false,
        };
    }

    renderIndents(){
        return _.map(_.range(this.props.node.data.depth), function(d, i){
            return <span key={i} className='nbsp'>&nbsp;</span>;
        });
    }

    handleEditClick(e){
        e.stopPropagation();
        this.setState({showForm: true});
    }

    handleCancel(e){
        e.stopPropagation();
        this.setState({showForm: false});
    }

    handleSave(e){
        e.stopPropagation();
        this.setState({showForm: false});
    }

    handleDelete(e){
        e.stopPropagation();
        this.setState({showForm: false});
    }

    renderDetail(){
        console.log(this.props.node)
        return (
            <p className='node'>
                {this.renderIndents()}
                {this.props.node.data.name}
            </p>
        );
    }

    renderForm(){
        return <EditNode
            node={this.props.node}
            parent={this.props.parent}
            handleCancel={this.handleCancel.bind(this)}
            handleSave={this.handleSave.bind(this)}
            handleDelete={this.handleDelete.bind(this)}
        />;
    }

    render() {
        let node = this.props.node,
            children = node.children || [];
        return (
            <div onClick={this.handleEditClick.bind(this)}>
                {
                    (this.state.showForm)?
                    this.renderForm():
                    this.renderDetail()
                }
                {children.map(function(child){
                    return <Node key={child.id} parent={node} node={child}/>;
                })}
            </div>
        );
    }
}

Node.propTypes = {
    node: React.PropTypes.object.isRequired,
    parent: React.PropTypes.object,
};

export default Node;
