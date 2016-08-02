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
            return <span key={i} className='nbsp'>&nbsp;&nbsp;</span>;
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

    handleUpdate(newNodeState){
        this.props.handleUpdate(this.props.node.id, newNodeState);
        this.setState({showForm: false});
    }

    handleDelete(e){
        e.stopPropagation();
        this.setState({showForm: false});
        this.props.handleDelete(this.props.node.id);
    }

    renderDetail(){
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
            parentOptions={this.props.parentOptions}
            parent={this.props.parent}
            handleCancel={this.handleCancel.bind(this)}
            handleUpdate={this.handleUpdate.bind(this)}
            handleDelete={this.handleDelete.bind(this)}
        />;
    }

    render() {
        let {node, sortableGroupDecorator} = this.props,
            children = node.children || [];

        return (
            <div onClick={this.handleEditClick.bind(this)} className='draggable' data-id={node.id}>
                {
                    (this.state.showForm)?
                    this.renderForm():
                    this.renderDetail()
                }
                <div ref={this.props.sortableGroupDecorator}>
                {children.map((child)=>{
                    return <Node
                        key={child.id}
                        parent={node.id}
                        node={child}
                        parentOptions={this.props.parentOptions}
                        handleUpdate={this.props.handleUpdate}
                        handleDelete={this.props.handleDelete}
                        sortableGroupDecorator={sortableGroupDecorator}
                        />;
                })}
                </div>
            </div>
        );
    }
}

Node.propTypes = {
    node: React.PropTypes.object.isRequired,
    parent: React.PropTypes.number.isRequired,
    parentOptions: React.PropTypes.array.isRequired,
    handleUpdate: React.PropTypes.func.isRequired,
    handleDelete: React.PropTypes.func.isRequired,
    sortableGroupDecorator: React.PropTypes.func.isRequired,
};

export default Node;
