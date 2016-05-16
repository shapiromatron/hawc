import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded, selectActive } from 'robAllTable/actions';
import Loading from 'shared/components/Loading';
import DomainCell from 'robAllTable/components/DomainCell';
import './AggregateGraph.css';


class AggregateGraph extends Component {

    componentWillMount(){
        let { dispatch, study_id } = this.props;
        dispatch(fetchStudyIfNeeded(study_id));
    }

    selectActiveWithName(domainName){
        // domainName is either {domain: xxx} or {domain: xxx, metric: xxx}
        this.props.dispatch(selectActive({...domainName}));
    }

    format_qualities(){
        let { qualities } = this.props;
        let domains = _.map(qualities, (quality) => {
            let score = quality;
            score.domain = quality.metric.domain.id;
            score.domain_text = quality.metric.domain.name;
            return score;
        });
        return d3.nest()
                 .key((d) => {return d.metric.domain.name;})
                 .entries(domains);
    }

    render(){
        let { itemsLoaded } = this.props;
        if (!itemsLoaded) return <Loading />;
        let domains = this.format_qualities();
        return (
            <div className='aggregate-graph'>
                <div className='aggregate-flex'>

                    {_.map(domains, (domain) => {
                        return <DomainCell key={domain.key}
                                   domain={domain}
                                   handleClick={this.selectActiveWithName.bind(this)}
                                   />;
                    })}
                </div>
                <div className='footer muted'>
                    Click on any cell above to view details.
                </div>
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        study_id: state.config.study.id,
        itemsLoaded: state.study.itemsLoaded,
        qualities: state.study.qualities,
        riskofbiases: state.study.riskofbiases,
    };
}

export default connect(mapStateToProps)(AggregateGraph);
