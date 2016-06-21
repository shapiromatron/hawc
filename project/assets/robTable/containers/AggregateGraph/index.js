import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded, selectActive } from 'robTable/actions';
import DisplayComponent from 'robTable/components/AggregateGraph';
import Loading from 'shared/components/Loading';


class AggregateGraph extends Component {

    componentWillMount(){
        this.props.dispatch(fetchStudyIfNeeded());
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
            <DisplayComponent domains={domains}
                              handleClick={this.selectActiveWithName.bind(this)}/>
        );
    }
}

function mapStateToProps(state){
    return {
        itemsLoaded: state.study.itemsLoaded,
        qualities: state.study.qualities,
        riskofbiases: state.study.riskofbiases,
    };
}

export default connect(mapStateToProps)(AggregateGraph);
