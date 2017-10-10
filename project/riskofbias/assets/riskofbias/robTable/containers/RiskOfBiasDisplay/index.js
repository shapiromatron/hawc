import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchFullStudyIfNeeded, selectActive } from 'riskofbias/robTable/actions';
import DisplayComponent from 'riskofbias/robTable/components/RiskOfBiasDisplay';
import ShowAll from 'riskofbias/robTable/components/ShowAll';
import Loading from 'shared/components/Loading';


class RiskOfBiasDisplay extends Component {

    constructor(props) {
        super(props);
        this.handleShowAllClick = this.handleShowAllClick.bind(this);
    }

    componentWillMount(){
        this.props.dispatch(fetchFullStudyIfNeeded());
    }

    isAllShown(){
        return this.props.active.length ===  this.props.riskofbiases.length;
    }

    handleShowAllClick(){
        let { dispatch } = this.props,
            domains = (this.isAllShown()) ? 'none': 'all';
        dispatch(selectActive({domain: domains}));
    }

    render(){

        let { itemsLoaded, active, config } = this.props;
        if (!itemsLoaded) return <Loading />;

        return (
            <div className='riskofbias-container'>
                <DisplayComponent active={active} config={config} />
                <ShowAll
                    allShown={this.isAllShown()}
                    handleClick={this.handleShowAllClick} />
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        itemsLoaded: state.study.itemsLoaded,
        active: state.study.active,
        riskofbiases: state.study.riskofbiases,
        config: state.config,
    };
}

export default connect(mapStateToProps)(RiskOfBiasDisplay);
