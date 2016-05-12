import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded } from 'robAllTable/actions';
import DomainDisplay from 'robAllTable/components/DomainDisplay';
import Loading from 'shared/components/Loading';


class RiskOfBiasDisplay extends Component {

    componentWillMount(){
        let { dispatch, study_id } = this.props;
        dispatch(fetchStudyIfNeeded(study_id));
    }

    format_riskofbiases(){
        let riskofbiases = _.filter(this.props.riskofbiases, (rob) => {return rob.active === true;});
        let domains = _.flatten(_.map(riskofbiases, (riskofbias) => {
            let author = riskofbias.author;
            return _.map(riskofbias.scores, (score) => {
                return Object.assign({}, score, {
                    author,
                    domain_name: score.metric.domain.name,
                    domain_id: score.metric.domain.id,
                });
            });
        }));
        return d3.nest()
            .key((d) => { return d.metric.domain.name;})
            .key((d) => {return d.metric.metric;})
            .entries(domains).reverse();
    }

    render(){
        let { itemsLoaded, riskofbiases } = this.props;
        if (!itemsLoaded) return <Loading />;
        let domains = this.format_riskofbiases();
        return (
            <div className='riskofbias-display'>
                    {_.map(domains, (domain) => {
                        return <DomainDisplay key={domain.key}
                                           domain={domain}
                                           domain_n={riskofbiases.length} />;
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
    };
}

export default connect(mapStateToProps)(RiskOfBiasDisplay);
