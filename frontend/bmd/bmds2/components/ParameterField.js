import React from "react";
import PropTypes from "prop-types";

class ParameterField extends React.Component {
    constructor(props) {
        super(props);
        this.selector = React.createRef();
        this.value = React.createRef();
    }

    handleChange(e) {
        let type = this.selector.current.value,
            value = type === "d" ? "" : parseFloat(this.value.current.value || 0);
        this.props.handleChange(`${type}|${value}`);
    }

    render() {
        let index = this.props.index,
            settings = this.props.settings,
            vals = this.props.value.split("|"),
            showInput = vals[0] === "d" ? "none" : "";

        return (
            <div className="form-group" key={index}>
                <label className="control-label">{settings.n}</label>
                <div className="controls">
                    <select
                        className="col-md-4"
                        style={{marginRight: "1em"}}
                        value={vals[0]}
                        ref={this.selector}
                        onChange={this.handleChange.bind(this)}>
                        <option value="d">Default</option>
                        <option value="s">Specified</option>
                        <option value="i">Initialized</option>
                    </select>
                    <input
                        style={{display: showInput}}
                        className="col-md-4"
                        type="number"
                        step="1e-8"
                        value={vals[1]}
                        ref={this.value}
                        onChange={this.handleChange.bind(this)}
                    />
                </div>
            </div>
        );
    }
}

ParameterField.propTypes = {
    index: PropTypes.number.isRequired,
    settings: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired,
    value: PropTypes.any.isRequired,
};

export default ParameterField;
