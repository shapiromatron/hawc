import React, { Component } from 'react';
import { connect } from 'react-redux';

import { checkScoreForUpdate } from 'robScoreCleanup/actions/Items';

import DisplayComponent from 'robScoreCleanup/components/ScoreList';


export class ScoreList extends Component {

    constructor(props) {
        super(props);
        this.handleCheck = this.handleCheck.bind(this);
    }

    handleCheck({target}) {
        this.props.dispatch(checkScoreForUpdate(target.id));
    }

    render() {
        if (!this.props.isLoaded) return null;
        let { items, idList, selected, config } = this.props,
            filteredItems = _.isEmpty(selected) ?
                items :
                _.filter(items,
                    (item) => { return _.contains(selected, item.score.toString()); });

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
    const { items, updateIds, isLoaded } = state.items;
    return {
        selected: state.scores.selected,
        items,
        idList: updateIds,
        isLoaded,
    };
}

export default connect(mapStateToProps)(ScoreList);
