import * as d3 from "d3";
import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {connect} from "react-redux";

import {fetchFullStudyIfNeeded, selectActive} from "riskofbias/robTable/actions";
import DisplayComponent from "riskofbias/robTable/components/AggregateGraph";
import Loading from "shared/components/Loading";

class AggregateGraph extends Component {
    constructor(props) {
        super(props);
        this.selectActiveWithName = this.selectActiveWithName.bind(this);
    }

    componentDidMount() {
        this.props.dispatch(fetchFullStudyIfNeeded());
    }

    selectActiveWithName(domainName) {
        // domainName is either {domain: xxx} or {domain: xxx, metric: xxx}
        this.props.dispatch(selectActive({...domainName}));
    }

    formatRiskofbiasForDisplay() {
        let domains = _.flattenDeep(
            _.map(this.props.riskofbiases, domain => {
                return _.map(domain.values, metric => {
                    return _.filter(metric.values, score => {
                        return score.final;
                    });
                });
            })
        );

        return d3
            .nest()
            .key(d => {
                return d.metric.domain.name;
            })
            .key(d => {
                return d.metric.name;
            })
            .entries(domains);
    }

    render() {
        let {itemsLoaded} = this.props;
        if (!itemsLoaded) return <Loading />;
        let domains = this.formatRiskofbiasForDisplay();
        return _.isEmpty(domains) ? (
            <NoFinalReviewWarning />
        ) : (
            <DisplayComponent domains={domains} handleClick={this.selectActiveWithName} />
        );
    }
}

const NoFinalReviewWarning = () => {
    return (
        <div className="container">
            <span className="alert alert-warning span12">
                A final reviewer assignment is required.
            </span>
        </div>
    );
};

function mapStateToProps(state) {
    return {
        itemsLoaded: state.study.itemsLoaded,
        riskofbiases: state.study.riskofbiases,
    };
}

AggregateGraph.propTypes = {
    dispatch: PropTypes.func,
    riskofbiases: PropTypes.array,
    itemsLoaded: PropTypes.bool,
};

export default connect(mapStateToProps)(AggregateGraph);
