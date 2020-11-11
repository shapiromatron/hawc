import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

class TagNode extends Component {
    constructor(props) {
        super(props);
        this.localStorageKey = `lit-referencetag-${props.tag.data.pk}-expanded`;
        this.state = {
            expanded: window.localStorage.getItem(this.localStorageKey) === "false" ? false : true,
        };
    }
    render() {
        const {tag, showReferenceCount, handleOnClick} = this.props;
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
                <p className="nestedTag" onClick={() => handleOnClick(tag)}>
                    {_.repeat("   ", tag.depth - 1)}
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
};

class TagTree extends Component {
    render() {
        const {tagtree, handleTagClick, showReferenceCount} = this.props;
        return (
            <div>
                {tagtree.rootNode.children.map((tag, i) => (
                    <TagNode
                        key={i}
                        tag={tag}
                        handleOnClick={handleTagClick}
                        showReferenceCount={showReferenceCount}
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
};
TagTree.defaultProps = {
    showReferenceCount: false,
    handleTagClick: h.noop,
};

export default TagTree;
