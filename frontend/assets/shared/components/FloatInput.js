import React, {Component} from "react";
import PropTypes from "prop-types";

class FloatInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            value: props.value.toString(),
        };
    }

    renderLabel() {
        if (!this.props.label) {
            return null;
        }
        return (
            <label htmlFor={`id_${this.props.name}`} className="control-label">
                {this.props.label}
                {this.props.required ? <span className="asteriskField">*</span> : null}
            </label>
        );
    }

    render() {
        return (
            <div className="form-group">
                {this.renderLabel()}
                <input
                    className="col-md-12"
                    id={`id_${this.props.name}`}
                    name={this.props.name}
                    type="text"
                    required={this.props.required}
                    value={this.state.value}
                    onBlur={e => {
                        let valueString = e.target.value,
                            valueFloat = parseFloat(valueString);
                        if (
                            isNaN(valueFloat) ||
                            (this.props.minimum && valueFloat < this.props.minimum) ||
                            (this.props.maximum && valueFloat > this.props.maximum)
                        ) {
                            this.setState({value: this.props.value.toString()});
                        } else {
                            this.props.onChange(e);
                            this.setState({value: valueFloat.toString()});
                        }
                    }}
                    onChange={e => this.setState({value: e.target.value})}
                />
                {this.props.helpText ? <p className="help-block">{this.props.helpText}</p> : null}
            </div>
        );
    }
}

FloatInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.number.isRequired,
    minimum: PropTypes.number,
    maximum: PropTypes.number,
};

export default FloatInput;
