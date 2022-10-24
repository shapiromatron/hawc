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
            tagClass = tag === selectedTag ? "d-flex nestedTag selected" : "d-flex nestedTag",
            hasChildren = tag.children.length > 0,
            expanderIcon = this.state.expanded ? "fa-minus" : "fa-plus",
            toggleExpander = e => {
                e.stopPropagation();
                const newValue = !this.state.expanded;
                window.localStorage.setItem(this.localStorageKey, newValue);
                this.setState({expanded: newValue});
            };

        return (
            <>
                <div className={tagClass} onClick={() => handleOnClick(tag)}>
                    <div style={{width: (tag.depth - 1) * 10 + 25}}>
                        {hasChildren ? (
                            <button
                                className="float-right btn btn-sm px-2"
                                onClick={toggleExpander}>
                                <i className={`fa ${expanderIcon}`}></i>
                            </button>
                        ) : null}
                    </div>
                    <div style={{flex: 1}}>
                        <span>
                            {tag.data.name}
                            {showReferenceCount ? ` (${tag.get_references_deep().length})` : null}
                        </span>
                    </div>
                </div>
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
            </>
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
        const {
            tagtree,
            handleTagClick,
            showReferenceCount,
            selectedTag,
            untaggedHandleClick,
            untaggedCount,
        } = this.props;
        return (
            <div
                className="resize-y p-2"
                style={{
                    maxHeight: "120vh",
                    height: "80vh",
                    backgroundColor: "aliceblue",
                    borderRadius: "7px",
                }}>
                {tagtree.rootNode.children.map((tag, i) => (
                    <TagNode
                        key={i}
                        tag={tag}
                        handleOnClick={handleTagClick}
                        showReferenceCount={showReferenceCount}
                        selectedTag={selectedTag}
                    />
                ))}
                {untaggedHandleClick ? (
                    <p className="nestedTag mt-2" onClick={untaggedHandleClick}>
                        Untagged References: ({untaggedCount})
                    </p>
                ) : null}
            </div>
        );
    }
}
TagTree.propTypes = {
    tagtree: PropTypes.object.isRequired,
    handleTagClick: PropTypes.func,
    showReferenceCount: PropTypes.bool,
    selectedTag: PropTypes.object,
    untaggedCount: PropTypes.number,
    untaggedHandleClick: PropTypes.func,
};
TagTree.defaultProps = {
    showReferenceCount: false,
    handleTagClick: h.noop,
};

export default TagTree;
