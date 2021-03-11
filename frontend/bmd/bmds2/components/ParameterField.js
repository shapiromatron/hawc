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
            <div className="row mb-2" key={index}>
                <div className="col-md-4">
                    <label>{settings.n}</label>
                </div>
                <div className="col-md-4">
                    <select
                        className="form-control"
                        style={{marginRight: "1em"}}
                        value={vals[0]}
                        ref={this.selector}
                        onChange={this.handleChange.bind(this)}>
                        <option value="d">Default</option>
                        <option value="s">Specified</option>
                        <option value="i">Initialized</option>
                    </select>
                </div>
                <div className="col-md-4">
                    <input
                        style={{display: showInput}}
                        className="form-control"
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
