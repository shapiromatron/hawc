import React, {Component} from "react";
import PropTypes from "prop-types";

class StudyLabel extends Component {
    render() {
        return (
            <div className={this.props.className}>
                <a href={this.props.study.url}>{this.props.study.short_citation}</a>
            </div>
        );
    }
}

StudyLabel.propTypes = {
    study: PropTypes.shape({
        url: PropTypes.string.isRequired,
        short_citation: PropTypes.string.isRequired,
    }).isRequired,
    className: PropTypes.string,
};

export default StudyLabel;
