import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import {param_cw} from "../constants";

const getText = function (model, k, v) {
    let def = model.defaults[k],
        tmp;
    switch (def.t) {
        case "i":
        case "d":
        case "dd":
        case "rp":
            return (
                <span>
                    <b>{def.n}:</b> {v}
                </span>
            );
        case "b":
            tmp = v === 1 ? "fa fa-check-square-o" : "fa fa-square-o";
            return (
                <span>
                    <b>{def.n}:</b> <i className={tmp} />
                </span>
            );
        case "p":
            v = v.split("|");
            return (
                <span>
                    <b>{def.n}:</b> {param_cw[v[0]]} to {v[1]}
                </span>
            );
        default:
            console.error(`Invalid type: ${model.t}`);
            return null;
    }
};

@inject("store")
@observer
class ModelOptionOverrideList extends React.Component {
    render() {
        const {index, store} = this.props,
            model = store.modelSettings[index];

        if (_.isEmpty(model.overrides)) {
            return <span>-</span>;
        } else {
            return (
                <ul>
                    {_.chain(model.overrides)
                        .toPairs()
                        .filter(d => model.defaults[d[0]].n !== undefined)
                        .map(d => <li key={d[0]}>{getText(model, d[0], d[1])}</li>)
                        .value()}
                </ul>
            );
        }
    }
}

ModelOptionOverrideList.propTypes = {
    index: PropTypes.number.isRequired,
    store: PropTypes.object,
};

export default ModelOptionOverrideList;
