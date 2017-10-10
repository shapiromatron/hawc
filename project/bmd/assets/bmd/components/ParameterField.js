import React from 'react';


class ParameterField extends React.Component {

    handleChange(e){
        let type = this.refs.selector.value,
            value = (type === 'd')? '': parseFloat(this.refs.value.value || 0);
        this.props.handleChange(`${type}|${value}`);
    }

    render() {

        let index = this.props.index,
            settings = this.props.settings,
            vals = this.props.value.split('|'),
            showInput = (vals[0] === 'd')? 'none': '';

        return (
            <div className="control-group" key={index}>
                <label className="control-label">{settings.n}</label>
                <div className="controls">
                    <select className="span4" style={{marginRight:'1em'}}
                        value={vals[0]} ref='selector'
                        onChange={this.handleChange.bind(this)}>
                        <option value="d">Default</option>
                        <option value="s">Specified</option>
                        <option value="i">Initialized</option>
                    </select>
                    <input
                        style={{display: showInput}}
                        className="span4" type="number" step="1e-8"
                        value={vals[1]} ref='value'
                        onChange={this.handleChange.bind(this)}></input>
                </div>
            </div>
        );
    }
}

ParameterField.propTypes = {
    index: React.PropTypes.number.isRequired,
    settings: React.PropTypes.object.isRequired,
    handleChange: React.PropTypes.func.isRequired,
    value: React.PropTypes.any.isRequired,
};

export default ParameterField;
