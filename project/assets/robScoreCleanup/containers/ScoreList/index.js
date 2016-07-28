import React, { Component } from 'react';
import { connect } from 'react-redux';

import { checkScoreForUpdate } from 'robScoreCleanup/actions/Items';

import CheckboxScoreDisplay from 'robScoreCleanup/components/CheckboxScoreDisplay';


export class ScoreList extends Component {

    constructor(props) {
        super(props);
        this.handleCheck = this.handleCheck.bind(this);
    }

    handleCheck({target}) {
        this.props.dispatch(checkScoreForUpdate(target.id));
    }

    render() {
        let { items, idList, selected } = this.props,
            filteredItems = _.isEmpty(selected) ?
                items :
                _.filter(items,
                    (item) => { return _.contains(selected, item.score.toString()); });

        return (
            <div>
            {_.map(filteredItems, (item) => {
                item = item.author ? item : Object.assign({}, item, {author: { full_name: ''}});
                let checked = _.contains(idList, item.id);
                return (
                    <div key={item.id}>
                        <CheckboxScoreDisplay
                            item={item}
                            config={this.props.config}
                            handleCheck={this.handleCheck}
                            checked={checked}/>
                        <hr/>
                    </div>
                    );
            })}
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        selected: state.scores.selected,
        items: state.items.items,
        idList: state.items.updateIds,
    };
}

export default connect(mapStateToProps)(ScoreList);
