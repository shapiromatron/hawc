import _ from 'underscore';
import React from 'react';
import PropTypes from 'prop-types';

import EditNode from './EditNode';


class Node extends React.Component {

    constructor() {
        super();
        this.state = {
            showForm: false,
            showChildren: true,
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

    toggleChildrenVisibility(e){
        e.stopPropagation();
        this.setState({showChildren: !this.state.showChildren});
    }

    renderShowHide(){
        let active = (this.props.node.children && this.props.node.children.length>0),
            classed = 'fa fa-fw',
            action = null;

        if (active){
            classed += (this.state.showChildren)?' fa-minus': ' fa-plus';
            action = this.toggleChildrenVisibility.bind(this);
        }

        return (
            <button
                className='btn btn-mini btn-link'
                title='Show/hide child nodes'
                onClick={action}>
                    <i className={classed}></i>
            </button>
        );
    }

    renderDetail(){


        return (
            <p className='node'>
                {this.renderIndents()}
                {this.renderShowHide()}
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
            children = node.children || [],
            displayChildren = (this.state.showChildren)? 'inherit': 'none';

        return (
            <div onClick={this.handleEditClick.bind(this)} className='draggable' data-id={node.id}>
                {
                    (this.state.showForm)?
                    this.renderForm():
                    this.renderDetail()
                }
                <div ref={this.props.sortableGroupDecorator}
                    style={{display: displayChildren}}>
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
    node: PropTypes.object.isRequired,
    parent: PropTypes.number.isRequired,
    parentOptions: PropTypes.array.isRequired,
    handleUpdate: PropTypes.func.isRequired,
    handleDelete: PropTypes.func.isRequired,
    sortableGroupDecorator: PropTypes.func.isRequired,
};

export default Node;
