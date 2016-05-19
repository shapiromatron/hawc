import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded, selectActive } from 'robTable/actions';
import DomainDisplay from 'robTable/components/DomainDisplay';
import ShowAll from 'robTable/components/ShowAll';
import Loading from 'shared/components/Loading';


class RiskOfBiasDisplay extends Component {

    componentWillMount(){
        let { dispatch, study_id } = this.props;
        dispatch(fetchStudyIfNeeded(study_id));

    }

    handleShowAllClick(){
        let { dispatch } = this.props;
        dispatch(selectActive({domain: 'all'}));
    }

    render(){
        let { itemsLoaded, active } = this.props;
        if (!itemsLoaded) return <Loading />;

        return (
            <div className='riskofbias-display'>
                {_.map(active, (domain) => {
                    return <DomainDisplay key={domain.key}
                                       domain={domain} />;
                })}
                <ShowAll handleClick={this.handleShowAllClick.bind(this)} />
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        study_id: state.config.study.id,
        itemsLoaded: state.study.itemsLoaded,
        riskofbiases: state.study.riskofbiases,
        active: state.study.active,
    };
}

export default connect(mapStateToProps)(RiskOfBiasDisplay);
