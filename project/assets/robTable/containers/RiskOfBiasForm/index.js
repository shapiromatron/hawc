import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded, submitRiskOfBiasScores } from 'robTable/actions';
import DomainDisplay from 'robTable/components/DomainDisplay';
import Loading from 'shared/components/Loading';
import ScrollToMessageBox from 'robTable/components/ScrollToMessageBox';
import ScrollToErrorBox from 'robTable/components/ScrollToErrorBox';
import './RiskOfBiasForm.css';


class RiskOfBiasForm extends Component {

    componentWillMount(){
        this.props.dispatch(fetchStudyIfNeeded());
    }

    submitForm(e){
        e.preventDefault();
        let scores = _.flatten(_.map(this.refs, (domain) => {
            return _.map(domain.refs, (metric) => {
                let { form } = metric.refs;
                return {
                    id: form.props.score.id,
                    notes: form.refs.notes.state.value,
                    score: form.refs.score.refs.select.value };
            });
        }));
        this.props.dispatch(submitRiskOfBiasScores({scores}));
    }

    handleCancel(e){
        e.preventDefault();
        window.location.href = this.props.config.cancelUrl;
    }

    render(){
        let { itemsLoaded, riskofbiases, error, message, config } = this.props;
        if (!itemsLoaded) return <Loading />;

        return (
            <div className='riskofbias-display'>
                { message ? <ScrollToMessageBox message={message} /> : null }
                { error ? <ScrollToErrorBox error={error} /> : null}
                <form action="">

                    {_.map(riskofbiases, (domain) => {
                        return <DomainDisplay key={domain.key}
                                           ref={domain.key}
                                           domain={domain}
                                           config={config} />;
                    })}
                    <button className='btn btn-primary'
                            onClick={this.submitForm.bind(this)}>
                        Update risk of bias
                    </button>
                    <button className='btn'
                            onClick={this.handleCancel.bind(this)}>Cancel</button>
                </form>
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        config: state.config,
        itemsLoaded: state.study.itemsLoaded,
        riskofbiases: state.study.riskofbiases,
        error: state.study.error,
        message: state.study.message,
    };
}


export default connect(mapStateToProps)(RiskOfBiasForm);
