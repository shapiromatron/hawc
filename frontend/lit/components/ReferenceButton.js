import PropTypes from "prop-types";
import React, {Component} from "react";
import ClipboardButton from "shared/components/ClipboardButton";

class ReferenceButton extends Component {
    render() {
        const {className, url, displayText, textToCopy} = this.props;
        return (
            <div className="btn-group mx-1">
                <a className={className} href={url} target="_blank" rel="noopener noreferrer">
                    {displayText}
                </a>
                <ClipboardButton textToCopy={textToCopy} className={className} />
            </div>
        );
    }
}
ReferenceButton.propTypes = {
    className: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
    displayText: PropTypes.string.isRequired,
    textToCopy: PropTypes.string.isRequired,
};

export default ReferenceButton;
