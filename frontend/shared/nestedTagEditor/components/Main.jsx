import "./Main.css";

import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";
import Sortable from "sortablejs";

import {NO_PARENT} from "../constants";
import EditNode from "./EditNode";
import Node from "./Node";

@inject("store")
@observer
class TagEditorMain extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchTags();
    }

    constructor() {
        super();
        this.state = {
            showCreate: false,
        };
    }

    sortableGroupDecorator = componentBackingInstance => {
        const {store} = this.props;
        // check if backing instance not null
        if (!componentBackingInstance) {
            return;
        }
        Sortable.create(componentBackingInstance, {
            draggable: ".draggable",
            ghostClass: "draggable-ghost",
            animation: 200,
            onUpdate: e => store.moveTag(parseInt(e.item.dataset.id), e.oldIndex, e.newIndex),
        });
    };

    render() {
        const {store} = this.props;

        if (!store.tagsLoaded) {
            return <Loading />;
        }

        return (
            <div>
                <h2 className="d-inline-block">{store.config.title}</h2>
                <button
                    onClick={() => this.setState({showCreate: true})}
                    className="float-right btn btn-primary">
                    <i className="fa fa-fw fa-plus" />
                    {store.config.btnLabel}
                </button>
                <p className="form-text text-muted">
                    <span
                        dangerouslySetInnerHTML={{
                            __html: store.config.extraHelpHtml,
                        }}
                    />
                    Click on any node to edit that node or move the node to a different parent. If
                    you move a node, by default the node will be the last-child to that parent. You
                    can also drag nodes to re-organize siblings.
                </p>
                <div>
                    {this.state.showCreate ? (
                        <EditNode
                            node={{
                                data: {
                                    name: "",
                                },
                                id: null,
                            }}
                            parent={NO_PARENT}
                            parentOptions={store.parentOptions}
                            handleCancel={() => {
                                this.setState({showCreate: false});
                            }}
                            handleCreate={newNode => {
                                this.setState({showCreate: false});
                                store.createTag(newNode);
                            }}
                        />
                    ) : null}
                    {store.tags.length === 0 ? (
                        <p className="form-text text-muted">
                            <i>No content is available - create some!</i>
                        </p>
                    ) : (
                        <div ref={this.sortableGroupDecorator}>
                            {store.tags.map(node => {
                                return (
                                    <Node
                                        key={node.id}
                                        node={node}
                                        parent={NO_PARENT}
                                        parentOptions={store.parentOptions}
                                        handleUpdate={(id, node) => store.updateTag(id, node)}
                                        handleDelete={id => store.deleteTag(id)}
                                        sortableGroupDecorator={this.sortableGroupDecorator.bind(
                                            this
                                        )}
                                    />
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

TagEditorMain.propTypes = {
    store: PropTypes.object,
};

export default TagEditorMain;
