import React, { Component } from 'react';
import PropTypes from 'prop-types';

class FinishedTaskFilter extends Component {

    render() {
        return (
            <div>
                <label>
                    <input type="checkbox"
                        name='filter'
                        style={{margin: '4px'}}
                        checked={this.props.checked}
                        onChange={this.props.onChange}/>
                    Hide completed and abandoned tasks
                </label>
            </div>
        );
    }
}

FinishedTaskFilter.propTypes = {
    checked: PropTypes.bool.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default FinishedTaskFilter;
