import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded, selectActive } from 'robTable/actions';
import DomainDisplay from 'robTable/components/DomainDisplay';
import ShowHideAll from 'robTable/components/ShowHideAll';
import Loading from 'shared/components/Loading';


class RiskOfBiasDisplay extends Component {

    componentWillMount(){
        let { dispatch, study_id } = this.props;
        dispatch(fetchStudyIfNeeded(study_id));
        this.setState({showHide: 'Hide'});
    }

    toggleShowHideAll(){
        let { dispatch, riskofbiases } = this.props;
        if (this.state.showHide == 'Hide'){
            dispatch(selectActive({domain: []}));
            this.setState({showHide: 'Show'});
        } else {
            dispatch(selectActive({domain: 'all'}));
            this.setState({showHide: 'Hide'});
        }
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
                <ShowHideAll actionText={this.state.showHide}
                             handleClick={this.toggleShowHideAll.bind(this)} />
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
