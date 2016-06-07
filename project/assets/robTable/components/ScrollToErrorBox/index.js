import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';

class ScrollToErrorBox extends Component {

    componentDidMount(){
        ReactDOM.findDOMNode(this).scrollIntoView(false);
    }

    render(){
        let { error } = this.props;
        if (error.detail){
            error = error.detail;
        } else if (error.message) {
            error = error.message;
        }
        return (
            <div className='alert alert-danger' >
                {error}
            </div>
        );

    }
}

ScrollToErrorBox.propTypes = {
    error: PropTypes.object,
};

export default ScrollToErrorBox;
