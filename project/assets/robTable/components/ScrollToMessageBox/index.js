import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';

class ScrollToMessageBox extends Component {

    componentDidMount(){
        ReactDOM.findDOMNode(this).scrollIntoView(false);
    }

    render(){
        let { message } = this.props;
        return (
            <div className='alert alert-success' >
                {message}
            </div>
        );
    }
}

ScrollToMessageBox.propTypes = {
    message: PropTypes.string,
};

export default ScrollToMessageBox;
