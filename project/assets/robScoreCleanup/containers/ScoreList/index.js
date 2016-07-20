import React, { Component } from 'react';
import { connect } from 'react-redux';

import { selectScoreForUpdate } from 'robScoreCleanup/actions/Items';

import CheckboxScoreDisplay from 'robScoreCleanup/components/CheckboxScoreDisplay';


export class ScoreList extends Component {

    constructor(props) {
        super(props);
        this.handleCheck = this.handleCheck.bind(this);
    }

    handleCheck({target}) {
        this.props.dispatch(selectScoreForUpdate(target.id));
    }

    render() {
        let { items, updateIds } = this.props;
        return (
            <div>
            {_.map(items, (item) => {
                item = item.author ? item : Object.assign({}, item, {author: { full_name: ''}});
                let checked = _.contains(updateIds, item.id);
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
    const { items, updateIds } = state.items;
    return {
        items,
        updateIds,
    };
}

export default connect(mapStateToProps)(ScoreList);
