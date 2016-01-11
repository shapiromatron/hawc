import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';
import { NICE, SUPER_NICE } from '../colors';
import { resetErrorMessage } from '../actions';
import ModelEndpointList from '../components/ModelEndpointList';

class Counter extends Component {
    constructor(props) {
        super(props);
        this.state = { counter: 0 };
        this.interval = setInterval(() => this.tick(), 1000);
        this.handleDismissClick = this.handleDismissClick.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }


    handleDismissClick(e){
        this.props.resetErrorMessage();
        e.preventDefault();
    }

    handleChange(nextValue){
        this.props.pushState(null, '/${nextValue}');
    }

    renderErrorMessage(){
        const { errorMessage } = this.props;
        if (!errorMessage){
            return null;
        }

        return (
            <p style={{ backgroundColor: '#e99', padding: 10 }}>
                <b>{errorMessage}</b>
                {' '}
                (<a href="#">
                    onClick={this.handleDismissClick}
                    Dismiss
                </a>)
            </p>
        );
    }

}

export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = { counter: 0 };
        this.handleDismissClick = this.handleDismissClick.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    handleDismissClick(e){
        this.props.resetErrorMessage();
        e.preventDefault();
    }

    handleChange(nextValue){
        this.props.pushState(null, '/${nextValue}');
    }

    renderErrorMessage(){
        const { errorMessage } = this.props;
        if (!errorMessage){
            return null;
        }

        return (
            <p style={{ backgroundColor: '#e99', padding: 10 }}>
                <b>{errorMessage}</b>
                {' '}
                (<a href="#">
                    onClick={this.handleDismissClick}
                    Dismiss
                </a>)
            </p>
        );
    }

    render() {
        const { children, inputValue } = this.props;

        return (
                <div>
                    <ModelEndpointList items={[
                        {
                            count: 2915,
                            type: "animal bioassay endpoints",
                            url: "http://127.0.0.1:8000/assessment/api/endpoints/ani/assessment_id=57",
                        },
                        {
                            count: 334,
                            type: "epidemiological outcomes assessed",
                            url: "http://127.0.0.1:8000/assessment/api/endpoints/epi/assessment_id=57",
                        },
                        {
                            count: 0,
                            type: "in vitro endpoints",
                            url: "http://127.0.0.1:8000/assessment/api/endpoints/invitro/assessment_id=57",
                        },
                    ]} model={"PFOA/PFOS Exposure and Immunotoxicity"} />
                    {children}
                </div>
        );
    }
}

App.propTypes = {
    errorMessage: PropTypes.string,
    resetErrorMessage: PropTypes.func.isRequired,
    pushState: PropTypes.func.isRequired,
    inputValue: PropTypes.string.isRequired,
    children: PropTypes.node,
};

function mapStateToProps(state){
    return {
        errorMessage: state.errorMessage,
        inputValue: state.router.location.pathname.substring(1),
    };
}

export default connect(mapStateToProps, {
    resetErrorMessage,
    pushState,
})(App);
