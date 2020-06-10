import React, {Component} from "react";
import PropTypes from "prop-types";

class IntInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            value: props.value.toString(),
        };
    }

    render() {
        return (
            <div className="control-group">
                <label htmlFor={`id_${this.props.name}`} className="control-label">
                    {this.props.label}
                    {this.props.required ? <span className="asteriskField">*</span> : null}
                </label>
                <div className="controls">
                    <input
                        className="span12"
                        id={`id_${this.props.name}`}
                        name={this.props.name}
                        type="text"
                        required={this.props.required}
                        value={this.state.value}
                        onBlur={e => {
                            let valueString = e.target.value,
                                valueInt = parseInt(valueString);
                            if (
                                isNaN(valueInt) ||
                                (this.props.minimum && valueInt < this.props.minimum) ||
                                (this.props.maximum && valueInt > this.props.maximum)
                            ) {
                                this.setState({value: this.props.value.toString()});
                            } else {
                                this.props.onChange(e);
                                this.setState({value: valueInt.toString()});
                            }
                        }}
                        onChange={e => this.setState({value: e.target.value})}
                    />
                    {this.props.helpText ? (
                        <p className="help-block">{this.props.helpText}</p>
                    ) : null}
                </div>
            </div>
        );
    }
}

IntInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.number.isRequired,
    minimum: PropTypes.number,
    maximum: PropTypes.number,
};

export default IntInput;
