import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
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
        const {tag, showReferenceCount, handleOnClick, selectedTag, showTagHover} = this.props,
            tagClass =
                tag === selectedTag
                    ? "d-flex nestedTag selected align-items-center"
                    : "d-flex nestedTag align-items-center",
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
                    <div
                        className="d-flex justify-content-end"
                        style={{width: (tag.depth - 1) * 10 + 25}}>
                        {hasChildren ? (
                            <button className="d-flex btn btn-sm px-1" onClick={toggleExpander}>
                                <i
                                    className={`fa ${expanderIcon}`}
                                    style={{fontSize: "0.8rem"}}></i>
                            </button>
                        ) : null}
                    </div>
                    <div className={showTagHover ? "tagName" : null} style={{flex: 1}}>
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
                              showTagHover={showTagHover}
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
    showTagHover: PropTypes.bool,
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
            showTagHover,
        } = this.props;
        return (
            <div id="litTagtree" className="resize-y p-2 mt-2">
                {tagtree.rootNode.children.map((tag, i) => (
                    <TagNode
                        key={i}
                        tag={tag}
                        handleOnClick={handleTagClick}
                        showReferenceCount={showReferenceCount}
                        selectedTag={selectedTag}
                        showTagHover={showTagHover}
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
    showTagHover: PropTypes.bool,
};
TagTree.defaultProps = {
    showReferenceCount: false,
    handleTagClick: h.noop,
    showTagHover: false,
};

export default TagTree;
