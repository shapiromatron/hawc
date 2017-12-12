import React, { Component } from 'react';
import PropTypes from 'prop-types';

import CheckboxScoreDisplay from 'riskofbias/robScoreCleanup/components/CheckboxScoreDisplay';


class ScoreList extends Component {

    constructor(props) {
        super(props);
    }

    render() {
        let { items, idList, config, handleCheck } = this.props;
        return (
             <div>
             <h4>RoB responses which meet criteria specified above:</h4>
            {_.map(items, (item) => {
                item = item.author ? item : Object.assign({}, item, {author: { full_name: ''}});
                let checked = _.includes(idList, item.id);
                return (
                    <div key={item.id}>
                        <CheckboxScoreDisplay
                            item={item}
                            config={config}
                            handleCheck={handleCheck}
                            checked={checked}/>
                        <hr/>
                    </div>
                    );
            })}
            </div>
        );
    }
}

ScoreList.propTypes = {
    handleCheck: PropTypes.func.isRequired,
    items: PropTypes.array.isRequired,
    idList: PropTypes.array.isRequired,
    config: PropTypes.object.isRequired,
};

export default ScoreList;
