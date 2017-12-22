import React from 'react';
import { connect } from 'react-redux';

import Loading from 'shared/components/Loading';
import Node from 'nestedTagEditor/components/Node';
import EditNode from 'nestedTagEditor/components/EditNode';
import Sortable from 'sortablejs';

import { createTag, updateTag, deleteTag, moveTag } from 'nestedTagEditor/actions';
import { NO_PARENT } from 'nestedTagEditor/constants';

class Tree extends React.Component {
    constructor() {
        super();
        this.state = {
            showCreate: false,
        };
    }

    handleUpdate(id, node) {
        this.props.dispatch(updateTag(id, node));
    }

    handleDelete(id) {
        this.props.dispatch(deleteTag(id));
    }

    renderNode(node) {
        return (
            <Node
                key={node.id}
                node={node}
                parent={NO_PARENT}
                parentOptions={this.props.parentOptions}
                handleUpdate={this.handleUpdate.bind(this)}
                handleDelete={this.handleDelete.bind(this)}
                sortableGroupDecorator={this.sortableGroupDecorator.bind(this)}
            />
        );
    }

    handleCreateClick() {
        this.setState({ showCreate: true });
    }

    handleCreateClickCancel() {
        this.setState({ showCreate: false });
    }

    handleCreate(newNode) {
        this.handleCreateClickCancel();
        this.props.dispatch(createTag(newNode));
    }

    renderCreateNode() {
        let newNode = {
            data: {
                name: '',
            },
            id: null,
        };

        return (
            <EditNode
                node={newNode}
                parent={NO_PARENT}
                parentOptions={this.props.parentOptions}
                handleCancel={this.handleCreateClickCancel.bind(this)}
                handleCreate={this.handleCreate.bind(this)}
            />
        );
    }

    renderNoTags() {
        if (this.props.tags.length > 0) {
            return;
        }
        return (
            <p className="help-block">
                <i>No content is available - create some!</i>
            </p>
        );
    }

    handleMoveNode(nodeId, oldIndex, newIndex) {
        this.props.dispatch(moveTag(nodeId, oldIndex, newIndex));
    }

    sortableGroupDecorator = (componentBackingInstance) => {
        // check if backing instance not null
        if (!componentBackingInstance) {
            return;
        }
        Sortable.create(componentBackingInstance, {
            draggable: '.draggable',
            ghostClass: 'draggable-ghost',
            chosenClass: 'draggable-chosen',
            animation: 200,
            onUpdate: (e) => {
                this.handleMoveNode(parseInt(e.item.dataset.id), e.oldIndex, e.newIndex);
            },
        });
    };

    render() {
        if (!this.props.tagsLoaded) {
            return <Loading />;
        }

        return (
            <div>
                <h1 key={0}>
                    {this.props.title}
                    <button
                        onClick={this.handleCreateClick.bind(this)}
                        className="pull-right btn btn-primary"
                    >
                        <i className="fa fa-fw fa-plus" />
                        {this.props.btnLabel}
                    </button>
                </h1>
                <p className="help-block">
                    <span
                        dangerouslySetInnerHTML={{
                            __html: this.props.extraHelpHtml,
                        }}
                    />
                    Click on any node to edit that node or move the node to a different parent. If
                    you move a node, by default the node will be the last-child to that parent. You
                    can also drag nodes to re-organize siblings.
                </p>
                <div>
                    {this.state.showCreate ? this.renderCreateNode() : null}
                    <div ref={this.sortableGroupDecorator}>
                        {this.props.tags.map(this.renderNode.bind(this))}
                    </div>
                    {this.renderNoTags()}
                </div>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        tagsLoaded: state.tree.tagsLoaded,
        tags: state.tree.tags,
        parentOptions: state.tree.parentOptions,
        title: state.config.title,
        extraHelpHtml: state.config.extraHelpHtml,
        btnLabel: state.config.btnLabel,
    };
}

export default connect(mapStateToProps)(Tree);
