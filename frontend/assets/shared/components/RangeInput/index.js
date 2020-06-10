import React, {Component} from "react";
import PropTypes from "prop-types";

class RangeInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            lower: props.value[0],
            upper: props.value[1],
        };
    }

    render() {
        return (
            <div className="control-group">
                <label htmlFor={`id_${this.props.name}`} className="control-label">
                    {this.props.label}
                    {this.props.required ? <span className="asteriskField">*</span> : null}
                </label>
                <div className="controls controls-row" id={`id_${this.props.name}`}>
                    <input
                        className="span6"
                        name={`${this.props.name}[0]`}
                        type="text"
                        required={this.props.required}
                        value={this.state.lower}
                        onBlur={this.props.onChange}
                        onChange={e => this.setState({lower: e.target.value})}
                    />
                    <input
                        className="span6"
                        name={`${this.props.name}[1]`}
                        type="text"
                        required={this.props.required}
                        value={this.state.upper}
                        onBlur={this.props.onChange}
                        onChange={e => this.setState({upper: e.target.value})}
                    />
                    {this.props.helpText ? (
                        <p className="help-block">{this.props.helpText}</p>
                    ) : null}
                </div>
            </div>
        );
    }
}

RangeInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.array.isRequired,
};

export default RangeInput;
