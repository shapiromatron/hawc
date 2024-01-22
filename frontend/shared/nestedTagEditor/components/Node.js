import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";

import EditNodeForm from "./EditNode";

class Node extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showForm: false,
            showChildren: true,
        };
    }

    render() {
        const {parent, parentOptions, node, handleDelete, handleUpdate, sortableGroupDecorator} =
                this.props,
            children = node.children || [],
            hasChildren = children.length > 0,
            displayChildren = this.state.showChildren ? "inherit" : "none",
            handleNodeClick = hasChildren
                ? event => {
                      event.stopPropagation();
                      this.setState({showChildren: !this.state.showChildren});
                  }
                : event => event.stopPropagation(),
            nodeClickIcon = hasChildren
                ? this.state.showChildren
                    ? "fa fa-fw fa-minus"
                    : "fa fa-fw fa-plus"
                : "fa fa-fw";

        return (
            <div
                onClick={event => {
                    event.stopPropagation();
                    this.setState({showForm: true});
                }}
                className="draggable"
                data-id={node.id}>
                {this.state.showForm ? (
                    <EditNodeForm
                        node={node}
                        parentOptions={parentOptions}
                        parent={parent}
                        handleCancel={event => {
                            event.stopPropagation();
                            this.setState({showForm: false});
                        }}
                        handleUpdate={newNodeState => {
                            handleUpdate(node.id, newNodeState);
                            this.setState({showForm: false});
                        }}
                        handleDelete={event => {
                            event.stopPropagation();
                            this.setState({showForm: false});
                            handleDelete(node.id);
                        }}
                    />
                ) : (
                    <p className="node">
                        <span
                            className="nbsp"
                            dangerouslySetInnerHTML={{
                                __html: _.repeat("&nbsp&nbsp;", node.data.depth),
                            }}></span>
                        {/* Always show button so tab-layout is preserved */}
                        <button
                            type="button"
                            className="btn btn-sm btn-link"
                            title="Show/hide child nodes"
                            style={hasChildren ? null : {pointerEvents: "none"}}
                            onClick={handleNodeClick}>
                            <i className={nodeClickIcon} />
                        </button>
                        {node.data.name}
                    </p>
                )}
                <div ref={this.props.sortableGroupDecorator} style={{display: displayChildren}}>
                    {children.map(child => {
                        return (
                            <Node
                                key={child.id}
                                parent={node.id}
                                node={child}
                                parentOptions={this.props.parentOptions}
                                handleUpdate={this.props.handleUpdate}
                                handleDelete={this.props.handleDelete}
                                sortableGroupDecorator={sortableGroupDecorator}
                            />
                        );
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
