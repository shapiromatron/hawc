import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded } from 'robTable/actions';
import DomainDisplay from 'robTable/components/DomainDisplay';
import Loading from 'shared/components/Loading';


class ConflictResolutionForm extends Component {

    componentWillMount(){
        let { dispatch, study_id } = this.props;
        dispatch(fetchStudyIfNeeded(study_id));
    }

    render(){
        let { itemsLoaded, riskofbiases, isForm } = this.props;
        if (!itemsLoaded) return <Loading />;

        return (
            <div className='riskofbias-display'>
                {_.map(riskofbiases, (domain) => {
                    return <DomainDisplay key={domain.key}
                                       domain={domain}
                                       isForm={isForm} />;
                })}
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        study_id: state.config.study.id,
        itemsLoaded: state.study.itemsLoaded,
        riskofbiases: state.study.riskofbiases,
        isForm: state.config.isForm,
    };
}


export default connect(mapStateToProps)(ConflictResolutionForm);
