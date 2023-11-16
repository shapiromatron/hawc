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
        const {tag, showReferenceCount, handleOnClick, selectedTag, showTagHoverAdd} = this.props,
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
                <div
                    className={"d-flex nestedTag align-items-center"}
                    onClick={() => handleOnClick(tag)}>
                    <div
                        className="d-flex justify-content-end"
                        style={{width: (tag.depth - 1) * 10 + 25}}>
                        {hasChildren ? (
                            <button
                                className="d-flex btn btn-sm px-1"
                                onClick={toggleExpander}
                                type="button">
                                <i
                                    className={`fa ${expanderIcon}`}
                                    style={{fontSize: "0.8rem"}}></i>
                            </button>
                        ) : null}
                    </div>
                    <div
                        className={(showTagHoverAdd ? "tagHoverAdd" : "tagHover").concat(
                            tag === selectedTag ? " tagSelected" : ""
                        )}
                        style={{flex: 1}}>
                        <span>
                            {tag.data.name}
                            {showReferenceCount ? (
                                <span className="ml-2 badge badge-dark">
                                    {tag.get_references_deep().length}
                                </span>
                            ) : null}
                            <span className="ml-2 badge badge-dark ids hidden">1{tag.data.pk}</span>
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
                              showTagHoverAdd={showTagHoverAdd}
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
    showTagHoverAdd: PropTypes.bool,
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
            showTagHoverAdd,
            untaggedReferencesSelected,
            style,
        } = this.props;
        return (
            <div id="litTagtree" className="resize-y p-2 mt-2" style={style}>
                {tagtree.rootNode.children.map((tag, i) => (
                    <TagNode
                        key={i}
                        tag={tag}
                        handleOnClick={handleTagClick}
                        showReferenceCount={showReferenceCount}
                        selectedTag={selectedTag}
                        showTagHoverAdd={showTagHoverAdd}
                    />
                ))}
                {untaggedHandleClick ? (
                    <p
                        className={`nestedTag mt-2 tagHover ${
                            untaggedReferencesSelected ? "tagSelected" : ""
                        }`}
                        onClick={untaggedHandleClick}>
                        Untagged References:
                        <span className="ml-2 badge badge-dark">{untaggedCount}</span>
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
    showTagHoverAdd: PropTypes.bool,
    untaggedReferencesSelected: PropTypes.bool,
    style: PropTypes.object,
};
TagTree.defaultProps = {
    showReferenceCount: false,
    handleTagClick: h.noop,
    showTagHoverAdd: false,
    untaggedReferencesSelected: false,
    style: {},
};

export default TagTree;
