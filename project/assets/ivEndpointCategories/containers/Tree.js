import React from 'react';
import { connect } from 'react-redux';

import Loading from 'shared/components/Loading';
import Node from 'ivEndpointCategories/components/Node';
import EditNode from 'ivEndpointCategories/components/EditNode';

import {
    createTag,
    updateTag,
    deleteTag,
} from 'ivEndpointCategories/actions';
import {
    NO_PARENT,
} from 'ivEndpointCategories/constants';


class Tree extends React.Component {

    constructor() {
        super();
        this.state = {
            showCreate: false,
        };
    }

    handleUpdate(id, node){
        this.props.dispatch(updateTag(id, node));
    }

    handleDelete(id){
        this.props.dispatch(deleteTag(id));
    }

    renderNode(node){
        return <Node
            key={node.id}
            node={node}
            parent={NO_PARENT}
            parentOptions={this.props.parentOptions}
            handleUpdate={this.handleUpdate.bind(this)}
            handleDelete={this.handleDelete.bind(this)} />;
    }

    handleCreateClick(){
        this.setState({showCreate: true});
    }

    handleCreateClickCancel(){
        this.setState({showCreate: false});
    }

    handleCreate(newNode){
        this.handleCreateClickCancel();
        this.props.dispatch(createTag(newNode));
    }

    renderCreateNode(){
        let newNode = {
            data: {
                name: '',
            },
            id: null,
        };

        return <EditNode
            node={newNode}
            parent={NO_PARENT}
            parentOptions={this.props.parentOptions}
            handleCancel={this.handleCreateClickCancel.bind(this)}
            handleCreate={this.handleCreate.bind(this)}
        />;
    }

    render() {
        if (!this.props.tagsLoaded){
            return <Loading />;
        }

        return <div>
            <h1 key={0}>
                Modify in-vitro endpoint categories
                <button
                    onClick={this.handleCreateClick.bind(this)}
                    className="pull-right btn btn-primary">Add new category</button>
            </h1>
            <div>
                {(this.state.showCreate)?this.renderCreateNode():null}
                {this.props.tags.map(this.renderNode.bind(this))}
            </div>
        </div>;
    }
}

function mapStateToProps(state) {
    return {
        tagsLoaded: state.tree.tagsLoaded,
        tags: state.tree.tags,
        parentOptions: state.tree.parentOptions,
    };
}

export default connect(mapStateToProps)(Tree);
