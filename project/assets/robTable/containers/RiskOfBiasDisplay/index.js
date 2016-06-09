import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchStudyIfNeeded, selectActive } from 'robTable/actions';
import DisplayComponent from 'robTable/components/RiskOfBiasDisplay';
import ShowAll from 'robTable/components/ShowAll';
import Loading from 'shared/components/Loading';


class RiskOfBiasDisplay extends Component {

    componentWillMount(){
        this.props.dispatch(fetchStudyIfNeeded());
    }

    handleShowAllClick(){
        let { dispatch } = this.props;
        dispatch(selectActive({domain: 'all'}));
    }

    render(){

        let { itemsLoaded, active, config } = this.props;
        if (!itemsLoaded) return <Loading />;

        return (
            <div className='riskofbias-container'>
                <DisplayComponent active={active} config={config} />
                <ShowAll handleClick={this.handleShowAllClick.bind(this)} />
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        itemsLoaded: state.study.itemsLoaded,
        active: state.study.active,
        config: state.config,
    };
}

export default connect(mapStateToProps)(RiskOfBiasDisplay);
