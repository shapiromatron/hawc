import React from 'react';


class ModelOptionField extends React.Component {

    renderInput(){
        let v = this.props.value,
            d = this.props.settings,
            handleChange = this.props.handleChange;

        switch (d.t){
        case 'i':
            return (
                <input className="span12" name={d.key} type="number"
                    onChange={handleChange} value={v}></input>
            );
        case 'd':
            return (
                <input className="span12" name={d.key} type="number"
                    onChange={handleChange} value={v} step="1e-8"></input>
            );
        case 'b':
            return (
                <input className="span12" name={d.key}  type="checkbox"
                    onChange={handleChange} checked={v}></input>
            );
        case 'dd':
            return (
                <input className="span12" name={d.key} type="number"
                    onChange={handleChange} value={v} type="text"></input>
            );
        case 'rp':
            return (
                <input className="span12" name={d.key} type="number"
                    onChange={handleChange} value={v} type="text"></input>
            );
        default:
            alert(`Invalid type: ${d.t}`);
            return null;
        }
    }

    render() {
        let {index, settings} = this.props;
        return (
            <div className="control-group" key={index}>
                <label className="control-label">{settings.n}</label>
                <div className="controls">
                    {this.renderInput()}
                </div>
            </div>
        );
    }
}

ModelOptionField.propTypes = {
    index: React.PropTypes.number.isRequired,
    settings: React.PropTypes.object.isRequired,
    handleChange: React.PropTypes.func.isRequired,
    value: React.PropTypes.any.isRequired,
};

export default ModelOptionField;
