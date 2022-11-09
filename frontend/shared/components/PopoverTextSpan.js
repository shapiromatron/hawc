import PropTypes from "prop-types";
import React, {Component} from "react";

import $ from "$";

class PopoverTextSpan extends Component {
    constructor(props) {
        super(props);
        this.ref = React.createRef();
    }

    componentDidMount() {
        $(this.ref.current).popover({
            placement: "top",
            trigger: "hover",
        });
    }

    render() {
        const {text, title, description} = this.props;
        return (
            <span ref={this.ref} className="popovers" data-title={title} data-content={description}>
                {text}
            </span>
        );
    }
}

PopoverTextSpan.propTypes = {
    text: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
};

export default PopoverTextSpan;
