import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';

class ScrollToErrorBox extends Component {

    componentDidMount(){
        ReactDOM.findDOMNode(this).scrollIntoView(false);
    }

    render(){
        let { error } = this.props;

        if (_.isNull(error)) {
            error;
        } else if (error.hasOwnProperty('detail')) {
            error = error.detail;
        } else if (error.hasOwnProperty('message')) {
            error = error.message;
        }

        if (!error) return <div></div>;
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
