import Clipboard from "clipboard";
import React, {Component} from "react";
import PropTypes from "prop-types";

class ClipboardButton extends Component {
    // copy text to clipboard
    constructor(props) {
        super(props);
        this.ref = React.createRef();
    }
    componentDidMount() {
        const {textToCopy} = this.props;
        this.clipboardEvent = new Clipboard(this.ref.current, {text: () => textToCopy});
    }
    componentWillUnmount() {
        this.clipboardEvent.destroy();
    }
    render() {
        const {className, textToCopy} = this.props;
        return (
            <button
                ref={this.ref}
                type="button"
                className={className}
                title={`Copy "${textToCopy}" to clipboard`}>
                <i className="fa fa-clipboard"></i>
            </button>
        );
    }
}

ClipboardButton.propTypes = {
    textToCopy: PropTypes.string.isRequired,
    className: PropTypes.string.isRequired,
};

export default ClipboardButton;
