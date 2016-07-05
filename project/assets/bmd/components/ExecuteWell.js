import React from 'react';


class ExecuteWell extends React.Component {

    render(){
        if (!this.props.editMode){
            return null;
        }

        return (
            <div className='well'>
                <button type='button'
                        className='btn btn-primary'
                        onClick={this.props.handleExecute}>Execute</button>
            </div>
        );
    }
}

ExecuteWell.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
    handleExecute: React.PropTypes.func.isRequired,
};

export default ExecuteWell;
