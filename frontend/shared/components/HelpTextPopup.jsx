import PropTypes from "prop-types";
import React, {Component} from "react";

import $ from "$";

const enablePopovers = $el => {
        $el.popover({
            placement: "auto",
            trigger: "hover",
            delay: {show: 100, hide: 1000},
        });
    },
    disablePopovers = $el => {
        $el.popover("dispose");
    };

class HelpTextPopover extends Component {
    constructor(props) {
        super(props);
        this.domNode = React.createRef();
    }
    componentDidMount() {
        enablePopovers($(this.domNode.current));
    }
    componentWillUnmount() {
        disablePopovers($(this.domNode.current));
    }
    render() {
        const {icon, title, content} = this.props;
        return (
            <i
                className={`ml-1 fa fa-fw ${icon}`}
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
    icon: PropTypes.string,
    title: PropTypes.string,
    content: PropTypes.string.isRequired,
};
HelpTextPopover.defaultProps = {
    icon: "fa-question-circle",
    title: "Help-text",
};

export {disablePopovers, enablePopovers};
export default HelpTextPopover;
