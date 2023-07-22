import _ from "lodash";
import React, {Component} from "react";
import ReactDOM from "react-dom";

import {NULL_VALUE} from "../summary/constants";
import config from "./config";

class ExtensionTableBody extends Component {
    render() {
        const items = [];
        _.forEach(config, (val, key) => {
            _.forEach(val.columns, col => {
                items.push({columnName: col, label: val.label});
            });
        });
        const sortedItems = _.sortBy(items, d => d.columnName.toLowerCase());
        return (
            <>
                {sortedItems.map((item, i) => {
                    return (
                        <tr key={i}>
                            <td>{item.columnName}</td>
                            <td>{item.label}</td>
                        </tr>
                    );
                })}
            </>
        );
    }
}

const getInteractivityOptions = function(columnNames) {
        const names = new Set(columnNames),
            options = [];
        _.forEach(config, (val, key) => {
            if (_.some(val.columns, item => names.has(item))) {
                options.push({id: key, label: val.label});
            }
        });
        options.unshift({id: NULL_VALUE, label: NULL_VALUE});
        return options;
    },
    renderExtensionTableBody = function(el) {
        ReactDOM.render(<ExtensionTableBody />, el);
    },
    _getId = (settings, data) => {
        for (const column of settings.columns) {
            const value = data[column];
            if (value) {
                return value;
            }
        }
    },
    showAsModal = (settings, data) => {
        const id = _getId(settings, data);
        settings.cls.displayAsModal(id);
    },
    getDetailUrl = (settings, data) => {
        const id = _getId(settings, data);
        return settings.cls.get_detail_url(id);
    };

export {getDetailUrl, getInteractivityOptions, renderExtensionTableBody, showAsModal};

// TODO - change back to array of items so we can have preferred order. throw error if duplicate keys
