import React, { Component } from 'react';
import { connect } from 'react-redux';

import {
    checkScoreForUpdate,
    updateVisibleItems,
} from 'robScoreCleanup/actions/Items';

import DisplayComponent from 'robScoreCleanup/components/ScoreList';


export class ScoreList extends Component {

    constructor(props) {
        super(props);
        this.handleCheck = this.handleCheck.bind(this);
    }

    componentWillReceiveProps(nextProps){
        if (nextProps.selected != this.props.selected ||
            nextProps.items != this.props.items){
            this.props.dispatch(updateVisibleItems(nextProps.selected));
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
            filteredItems = items.filter((d)=>_.contains(visibleItemIds, d.id));

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
        selected: state.scores.selected,
        items,
        visibleItemIds,
        idList: updateIds,
        isLoaded,
    };
}

export default connect(mapStateToProps)(ScoreList);
