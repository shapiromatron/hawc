import React, { Component } from 'react';
import { connect } from 'react-redux';

import {
    checkScoreForUpdate,
    updateVisibleItems,
} from 'riskofbias/robScoreCleanup/actions/Items';

import DisplayComponent from 'riskofbias/robScoreCleanup/components/ScoreList';


export class ScoreList extends Component {

    constructor(props) {
        super(props);
        this.handleCheck = this.handleCheck.bind(this);
    }

    componentWillReceiveProps(nextProps){
        if (nextProps.selectedScores != this.props.selectedScores ||
            nextProps.items != this.props.items ||
            nextProps.selectedStudies != this.props.selectedStudies){
            this.props.dispatch(updateVisibleItems(nextProps.selectedScores, nextProps.selectedStudies));
        }
    }

    handleCheck({target}) {
        this.props.dispatch(checkScoreForUpdate(target.id));
    }

    renderEmptyScoreList(){
        return <p className='lead'>No items meet your criteria.</p>;
    }

    render() {
        if (!this.props.isLoaded) return null;
        let { items, visibleItemIds, idList, config } = this.props,
            filteredItems = items.filter((d)=>_.includes(visibleItemIds, d.id));

        if (filteredItems.length === 0){
            return this.renderEmptyScoreList();
        }

        return (
            <DisplayComponent
                idList={idList}
                items={filteredItems}
                config={config}
                handleCheck={this.handleCheck} />
        );
    }
}

function mapStateToProps(state) {
    const { items, visibleItemIds, updateIds, isLoaded } = state.items;
    return {
        selectedScores: state.scores.selected,
        selectedStudies: state.studyTypes.selected,
        items,
        visibleItemIds,
        idList: updateIds,
        isLoaded,
    };
}

export default connect(mapStateToProps)(ScoreList);
