import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";

class QuillTextInput extends Component {
    /**
     * Wraps ReactQuill to add a hidden named textarea input for form submission.
     *
     */

    onChange = value => {
        this.props.onChange({target: {name: this.props.name, value}});
    };

    render() {
        return (
            <div className="control-group">
                <label htmlFor={`id_${this.props.name}`} className="control-label">
                    {this.props.label}
                    {this.props.required ? <span className="asteriskField">*</span> : null}
                </label>
                <div className="controls">
                    <ReactQuill
                        className="span12 textarea"
                        id={`id_${this.props.name}`}
                        type="text"
                        required={this.props.required}
                        value={this.props.value}
                        onChange={this.onChange}
                    />
                    <textarea
                        name={this.props.name}
                        value={this.props.value}
                        style={{display: "none"}}
                    />
                    {this.props.helpText ? (
                        <p className="help-block">{this.props.helpText}</p>
                    ) : null}
                </div>
            </div>
        );
    }
}

QuillTextInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    name: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
};

export default QuillTextInput;
