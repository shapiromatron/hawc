import React from 'react';
import PropTypes from 'prop-types';

class ModelOptionField extends React.Component {
    renderInput() {
        let v = this.props.value,
            d = this.props.settings,
            handleChange = this.props.handleChange;

        switch (d.t) {
            case 'i':
                return (
                    <input
                        className="span12"
                        name={d.key}
                        type="number"
                        onChange={handleChange}
                        value={v}
                    />
                );
            case 'd':
                return (
                    <input
                        className="span12"
                        name={d.key}
                        type="number"
                        onChange={handleChange}
                        value={v}
                        step="1e-8"
                    />
                );
            case 'b':
                return (
                    <input
                        className="span12"
                        name={d.key}
                        type="checkbox"
                        onChange={handleChange}
                        checked={v}
                    />
                );
            case 'dd':
                return (
                    <input
                        className="span12"
                        name={d.key}
                        type="number"
                        onChange={handleChange}
                        value={v}
                        type="text"
                    />
                );
            case 'rp':
                return (
                    <input
                        className="span12"
                        name={d.key}
                        type="number"
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
        let { index, settings } = this.props;
        return (
            <div className="control-group" key={index}>
                <label className="control-label">{settings.n}</label>
                <div className="controls">{this.renderInput()}</div>
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
