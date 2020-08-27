import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

class TagNode extends Component {
    constructor(props) {
        super(props);
        this.localStorageKey = `lit-referencetag-${props.tag.data.pk}-expanded`;
        this.state = {
            expanded: window.localStorage.getItem(this.localStorageKey) === "false" ? false : true,
        };
    }
    render() {
        const {tag, showReferences, handleOnClick} = this.props;
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
                        <span className={this.state.expanded ? "icon-minus" : "icon-plus"}></span>
                    </span>
                ) : null}
                <p className="nestedTag" onClick={() => handleOnClick(tag)}>
                    {_.repeat("   ", tag.depth - 1)}
                    {tag.data.name}
                    {showReferences ? ` (${tag.get_references_deep().length})` : null}
                </p>
                {this.state.expanded
                    ? tag.children.map((tag, i) => (
                          <TagNode key={i} tag={tag} handleOnClick={handleOnClick} />
                      ))
                    : null}
            </div>
        );
    }
}
TagNode.propTypes = {
    tag: PropTypes.object.isRequired,
    handleOnClick: PropTypes.func.isRequired,
    showReferences: PropTypes.bool,
};

TagNode.defaultProps = {
    showReferences: true,
};

class TagTree extends Component {
    render() {
        const {tagtree, handleTagClick} = this.props;
        return (
            <div>
                {tagtree.rootNode.children.map((tag, i) => (
                    <TagNode key={i} tag={tag} handleOnClick={handleTagClick} />
                ))}
            </div>
        );
    }
}
TagTree.propTypes = {
    tagtree: PropTypes.object.isRequired,
    handleTagClick: PropTypes.func.isRequired,
};

export default TagTree;
