import $ from "$";
import React, {Component} from "react";
import PropTypes from "prop-types";

class HelpTextPopover extends Component {
    constructor(props) {
        super(props);
        this.domNode = React.createRef();
    }
    componentDidMount() {
        $(this.domNode.current).popover({placement: "auto", trigger: "hover"});
    }
    componentWillUnmount() {
        $(this.domNode.current).popover("dispose");
    }
    render() {
        const {title, content} = this.props;
        return (
            <i
                className="ml-1 fa fa-fw fa-question-circle"
                ref={this.domNode}
                aria-hidden="true"
                data-html="true"
                data-toggle="popover"
                title={title}
                data-content={content}></i>
        );
    }
}

HelpTextPopover.propTypes = {
    title: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
};

export default HelpTextPopover;
