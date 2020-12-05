import React from "react";
import PropTypes from "prop-types";

class ModelOptionField extends React.Component {
    renderInput() {
        let v = this.props.value,
            d = this.props.settings,
            handleChange = this.props.handleChange;

        switch (d.t) {
            case "i":
                return (
                    <input
                        className="form-control"
                        name={d.key}
                        type="number"
                        onChange={handleChange}
                        value={v}
                    />
                );
            case "d":
                return (
                    <input
                        className="form-control"
                        name={d.key}
                        type="number"
                        onChange={handleChange}
                        value={v}
                        step="1e-8"
                    />
                );
            case "b":
                return (
                    <input
                        className="form-check-input"
                        name={d.key}
                        type="checkbox"
                        onChange={handleChange}
                        checked={v}
                    />
                );
            case "dd":
                return (
                    <input
                        className="form-control"
                        name={d.key}
                        onChange={handleChange}
                        value={v}
                        type="text"
                    />
                );
            case "rp":
                return (
                    <input
                        className="form-control"
                        name={d.key}
                        onChange={handleChange}
                        value={v}
                        type="text"
                    />
                );
            default:
                alert(`Invalid type: ${d.t}`);
                return null;
        }
    }

    render() {
        let {index, settings} = this.props;
        return settings.t === "b" ? (
            <div className="form-group form-check" key={index}>
                {this.renderInput()}
                <label className="form-check-label">{settings.n}</label>
            </div>
        ) : (
            <div className="form-group" key={index}>
                <label>{settings.n}</label>
                {this.renderInput()}
            </div>
        );
    }
}

ModelOptionField.propTypes = {
    index: PropTypes.number.isRequired,
    settings: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired,
    value: PropTypes.any.isRequired,
};

export default ModelOptionField;
