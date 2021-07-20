import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import h from "shared/utils/helpers";

@observer
class TagNode extends Component {
    constructor(props) {
        super(props);
        this.localStorageKey = `lit-referencetag-${props.tag.data.pk}-expanded`;
        this.state = {
            expanded: window.localStorage.getItem(this.localStorageKey) === "false" ? false : true,
        };
    }
    render() {
        const {tag, showReferenceCount, handleOnClick, selectedTag} = this.props,
            tagClass = tag === selectedTag ? "nestedTag selected" : "nestedTag";

        return (
            <div>
                {tag.children.length > 0 ? (
                    <span
                        className="nestedTagCollapser"
                        onClick={() => {
                            const newValue = !this.state.expanded;
                            window.localStorage.setItem(this.localStorageKey, newValue);
                            this.setState({expanded: newValue});
                        }}>
                        <span className={this.state.expanded ? "fa fa-minus" : "fa fa-plus"}></span>
                    </span>
                ) : null}
                <p
                    className={tagClass}
                    style={{paddingLeft: 2 + tag.depth * 13}}
                    onClick={() => handleOnClick(tag)}>
                    {tag.data.name}
                    {showReferenceCount ? ` (${tag.get_references_deep().length})` : null}
                </p>
                {this.state.expanded
                    ? tag.children.map((tag, i) => (
                          <TagNode
                              key={i}
                              tag={tag}
                              handleOnClick={handleOnClick}
                              showReferenceCount={showReferenceCount}
                              selectedTag={selectedTag}
                          />
                      ))
                    : null}
            </div>
        );
    }
}
TagNode.propTypes = {
    tag: PropTypes.object.isRequired,
    handleOnClick: PropTypes.func.isRequired,
    showReferenceCount: PropTypes.bool.isRequired,
    selectedTag: PropTypes.object,
};

@observer
class TagTree extends Component {
    render() {
        const {tagtree, handleTagClick, showReferenceCount, selectedTag} = this.props;
        return (
            <div style={{maxHeight: "80vh", overflowY: "scroll"}}>
                {tagtree.rootNode.children.map((tag, i) => (
                    <TagNode
                        key={i}
                        tag={tag}
                        handleOnClick={handleTagClick}
                        showReferenceCount={showReferenceCount}
                        selectedTag={selectedTag}
                    />
                ))}
            </div>
        );
    }
}
TagTree.propTypes = {
    tagtree: PropTypes.object.isRequired,
    handleTagClick: PropTypes.func,
    showReferenceCount: PropTypes.bool,
    selectedTag: PropTypes.object,
};
TagTree.defaultProps = {
    showReferenceCount: false,
    handleTagClick: h.noop,
};

export default TagTree;
