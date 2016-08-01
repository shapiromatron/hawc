import React from 'react';
import { connect } from 'react-redux';

import Loading from 'shared/components/Loading';
import Node from 'ivEndpointCategories/components/Node';

import {
    createTag,
    updateTag,
    deleteTag,
} from 'ivEndpointCategories/actions';


class Tree extends React.Component {

    handleCreate(){
        this.props.dispatch(createTag());
    }

    handleUpdate(id, name){
        this.props.dispatch(updateTag(id, name));
    }

    handleDelete(id){
        this.props.dispatch(deleteTag(id));
    }

    renderNode(node){
        return <Node
            key={node.id}
            node={node}
            handleUpdate={this.handleUpdate.bind(this)}
            handleDelete={this.handleDelete.bind(this)} />;
    }

    render() {
        if (!this.props.tagsLoaded){
            return <Loading />;
        }

        return <div>
            <h1 key={0}>
                Modify in-vitro endpoint categories
                <button
                    onClick={this.handleCreate.bind(this)}
                    className="pull-right btn btn-primary">Add new category</button>
            </h1>
            <div>
                {this.props.tags.map(this.renderNode.bind(this))}
            </div>
        </div>;
    }
}

function mapStateToProps(state) {
    return {
        tagsLoaded: state.tree.tagsLoaded,
        tags: state.tree.tags,
    };
}

export default connect(mapStateToProps)(Tree);
