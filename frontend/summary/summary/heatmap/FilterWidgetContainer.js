import h from "shared/utils/helpers";
import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {NULL_VALUE} from "../../summary/constants";
import DataPivotExtension from "summary/dataPivot/DataPivotExtension";

@observer
class FilterWidget extends Component {
    constructor(props) {
        super(props);
        this.renderItem = this.renderItem.bind(this);
    }
    render() {
        const {widget, numWidgets} = this.props,
            {colorScale, maxValue} = this.props.store,
            maxHeight = `${Math.floor((1 / numWidgets) * 100)}vh`,
            {selectAllFilterWidget, selectNoneFilterWidget} = this.props.store,
            data = this.props.store.getTableData,
            availableItems = _.chain(data)
                .map(d => d[widget.column])
                .map(d => (widget.delimiter ? d.split(widget.delimiter) : d))
                .flatten()
                .uniq()
                .value(),
            itemStore = this.props.store.filterWidgetState[widget.column],
            hiddenItems = _.chain(itemStore)
                .keys()
                .filter(d => itemStore[d] === false)
                .value(),
            showClickEvent = widget.on_click_event !== NULL_VALUE,
            items = _.sortedUniq([...availableItems, ...hiddenItems].sort());

        return (
            <div
                style={{
                    maxHeight,
                    padding: "10px 0",
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                }}>
                <div
                    style={{
                        backgroundColor: colorScale(maxValue),
                        color: h.getTextContrastColor(colorScale(maxValue)),
                        padding: "2px 10px",
                        flex: 0,
                    }}>
                    <h4>
                        {widget.column}
                        <div className="btn-group pull-right">
                            <button
                                className="btn btn-small"
                                onClick={() => selectAllFilterWidget(widget.column)}
                                title="Select all items">
                                <i className="fa fa-check-circle"></i>
                            </button>
                            <button
                                className="btn btn-small"
                                onClick={() => selectNoneFilterWidget(widget.column)}
                                title="De-select all items">
                                <i className="fa fa-times-circle"></i>
                            </button>
                        </div>
                    </h4>
                </div>
                <div
                    style={{
                        overflowY: "auto",
                        flex: 1,
                    }}>
                    {items
                        .sort()
                        .map((item, index) =>
                            this.renderItem(widget, item, index, itemStore, showClickEvent)
                        )}
                </div>
            </div>
        );
    }

    renderItem(widget, item, index, itemStore, showClickEvent) {
        const {toggleItemSelection, colorScale} = this.props.store,
            data = this.props.store.getTableData,
            numItems = data.filter(d =>
                widget.delimiter
                    ? _.includes(d[widget.column].split(widget.delimiter), item)
                    : d[widget.column] === item
            ).length;
        return (
            <div key={index}>
                {this.renderButton(widget, item, showClickEvent)}
                <label className="checkbox">
                    <div
                        style={{
                            backgroundColor: colorScale(numItems),
                            color: h.getTextContrastColor(colorScale(numItems)),
                            display: "inline-flex",
                            height: "1.5em",
                            width: "2.5em",
                            justifyContent: "center",
                            alignItems: "center",
                        }}>
                        <span>{numItems}</span>
                    </div>
                    <input
                        checked={itemStore[item]}
                        type="checkbox"
                        onChange={function(e) {
                            toggleItemSelection(widget.column, item, e.target.checked);
                        }}
                    />
                    <span>&nbsp;{item == "" ? "<null>" : item}</span>
                </label>
            </div>
        );
    }

    renderButton(widget, item, showClickEvent) {
        if (!showClickEvent) {
            return null;
        }
        const {showModalClick} = this.props.store,
            modalTarget = _.find(DataPivotExtension.values, {_dpe_name: widget.on_click_event})
                ._dpe_key,
            modalRows = _.chain(this.props.store.dataset)
                .filter({
                    [widget.column]: item,
                })
                .uniqBy(modalTarget)
                .sortBy(modalTarget)
                .value();
        // If there are no results disable button
        if (modalRows.length == 0) {
            return (
                <button
                    className="btn btn-mini pull-right disabled"
                    title="No additional information">
                    <i className="icon-eye-close"></i>
                </button>
            );
        }
        // If there are too many results disable button
        else if (modalRows.length > 10) {
            return (
                <button className="btn btn-mini pull-right disabled" title="Too many results">
                    <i className="icon-eye-open"></i>
                </button>
            );
        }
        // If there is one result link it to the button
        else if (modalRows.length == 1) {
            return (
                <button
                    className="btn btn-mini pull-right"
                    onClick={() => showModalClick(widget.on_click_event, modalRows[0])}
                    title="View additional information">
                    <i className="icon-eye-open"></i>
                </button>
            );
        }
        // If there are multiple results make the button a dropdown
        else {
            return (
                <div className="btn-group pull-right">
                    <a
                        className="btn btn-mini dropdown-toggle"
                        data-toggle="dropdown"
                        href="#"
                        title="View additional information">
                        <span className="caret"></span>
                        <i className="icon-eye-open"></i>
                    </a>
                    <ul className="dropdown-menu">
                        <li className="nav-header">{modalTarget}</li>
                        <li className="divider"></li>
                        {modalRows.map((row, idx) => {
                            return (
                                <li key={idx}>
                                    <a
                                        href="#"
                                        onClick={() => showModalClick(widget.on_click_event, row)}>
                                        {row[modalTarget]}
                                    </a>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            );
        }
    }
}
FilterWidget.propTypes = {
    store: PropTypes.object.isRequired,
    widget: PropTypes.object.isRequired,
    numWidgets: PropTypes.number.isRequired,
};

@inject("store")
@observer
class FilterWidgetContainer extends Component {
    render() {
        const {store} = this.props,
            {filter_widgets} = this.props.store.settings;
        return (
            <div style={{display: "flex", flexDirection: "column", width: "100%"}}>
                {filter_widgets.map((widget, idx) => (
                    <FilterWidget
                        key={idx}
                        store={store}
                        widget={widget}
                        numWidgets={filter_widgets.length}
                    />
                ))}
            </div>
        );
    }
}
FilterWidgetContainer.propTypes = {
    store: PropTypes.object,
};

export default FilterWidgetContainer;
