import React from 'react';


class ExecuteWell extends React.Component {

    renderValidationWarnings(){
        let {validationErrors} = this.props;
        if (validationErrors.length === 0) return null;

        return (
            <div className='alert alert-danger' style={{marginTop: '1em'}}>
                <b>The following validation warnings were found:</b>
                <ul>
                    {validationErrors.map((d, i)=>{
                        return <li key={i}>{d}</li>;
                    })}
                </ul>
            </div>
        );
    }

    renderExecuteButton(){
        if (this.props.isExecuting){
            return null;
        }
        return (
            <button type='button'
                    className='btn btn-primary'
                    onClick={this.props.handleExecute}>Execute</button>
        );
    }

    renderRunningIndicator(){
        if (!this.props.isExecuting){
            return null;
        }
        return (
            <p>
                <b>BMD executing, please wait...</b>
                <i className="fa fa-spinner fa-spin fa-3x fa-fw"></i>
            </p>
        );
    }

    render(){
        if (!this.props.editMode){
            return null;
        }
        return (
            <div className='well' style={{marginTop: '1em'}}>
                {this.renderExecuteButton.bind(this)()}
                {this.renderRunningIndicator.bind(this)()}
                {this.renderValidationWarnings.bind(this)()}
            </div>
        );
    }
}

ExecuteWell.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
    handleExecute: React.PropTypes.func.isRequired,
    validationErrors: React.PropTypes.array.isRequired,
    isExecuting: React.PropTypes.bool.isRequired,
};

export default ExecuteWell;
