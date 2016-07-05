import React from 'react';


class ExecuteWell extends React.Component {

    render(){
        if (!this.props.editMode){
            return null;
        }

        return (
            <div className='well'>
                <a className='btn btn-primary'>Execute</a>
            </div>
        );
    }
}

ExecuteWell.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
    handleExecute: React.PropTypes.func.isRequired,
};

export default ExecuteWell;
