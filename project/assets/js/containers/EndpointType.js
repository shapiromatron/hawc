import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';
import EndpointTypeList from '../components/EndpointTypeList';

function loadData(props) {
    const { assessment_id } = props;
    props.loadEndpointTypes(assessment_id);
}

export default class EndpointType extends Component {
    constructor(props) {
        super(props);
        this.renderEndpointTypes = this.renderEndpointTypes.bind(this);
        this.handleDismissClick = this.handleDismissClick.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    componentWillMount(){
        loadData(this.props);
    }

    componentWillReceiveProps(nextProps){
        if (nextProps.assessment_id !== this.props.assessment_id){
            loadData(nextProps);
        }
    }

    handleDismissClick(e){
        this.props.resetErrorMessage();
        e.preventDefault();
    }

    handleChange(nextValue){
        this.props.pushState(null, '/${nextValue}');
    }

    renderEndpointTypes(endpointTypes){

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
                    <EndpointTypeList items={[
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

EndpointType.propTypes = {
    errorMessage: PropTypes.string,
    resetErrorMessage: PropTypes.func.isRequired,
    pushState: PropTypes.func.isRequired,
    loadEndpointTypes: PropTypes.func.isRequired,
    endpointTypes: PropTypes.array,
    loadModelName: PropTypes.func.isRequired,
    modelName: PropTypes.string.isRequired,
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
})(EndpointType);
