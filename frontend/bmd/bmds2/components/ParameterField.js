import PropTypes from "prop-types";
import React from "react";

import h from "/shared/utils/helpers";

class ParameterField extends React.Component {
    constructor(props) {
        super(props);
        this.selector = React.createRef();
        this.value = React.createRef();
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
                        onChange={h.noop}>
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
                        onChange={h.noop}
                    />
                </div>
            </div>
        );
    }
}

ParameterField.propTypes = {
    index: PropTypes.number.isRequired,
    settings: PropTypes.object.isRequired,
    value: PropTypes.any.isRequired,
};

export default ParameterField;
