import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import h from "shared/utils/helpers";

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
                .map(d => (widget.delimiter && d ? d.split(widget.delimiter) : d))
                .flatten()
                .uniq()
                .value(),
            itemStore = this.props.store.filterWidgetState[widget.column],
            hiddenItems = _.chain(itemStore)
                .keys()
                .filter(d => itemStore[d] === false)
                .value(),
            filterWidgetExtension = this.props.store.extensions.filterWidgets[widget.column],
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
                        {h.titleCase(widget.column)}
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
                            this.renderItem(widget, item, index, itemStore, filterWidgetExtension)
                        )}
                </div>
            </div>
        );
    }

    renderItem(widget, item, index, itemStore, filterWidgetExtension) {
        const {toggleItemSelection, colorScale} = this.props.store,
            data = this.props.store.getTableData,
            numItems = data.filter(d =>
                widget.delimiter && d[widget.column]
                    ? _.includes(d[widget.column].split(widget.delimiter), item)
                    : d[widget.column] === item
            ).length;
        return (
            <div key={index}>
                {filterWidgetExtension && filterWidgetExtension.hasModal
                    ? this.renderButton(widget, item)
                    : null}
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

    renderButton(widget, item) {
        const extensions = this.props.store.extensions.filterWidgets,
            {showModalOnRow} = this.props.store,
            extension = extensions[widget.column],
            row_key = extension._dpe_key,
            modalRows = _.chain(this.props.store.dataset)
                .filter({
                    [widget.column]: item,
                })
                .uniqBy(row_key)
                .sortBy(row_key)
                .value();

        // If there are no results disable button
        if (modalRows.length == 0) {
            return (
                <button className="btn btn-mini pull-right disabled" title="No content found">
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
                    onClick={() => showModalOnRow(extension, modalRows[0])}
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
                        <li className="nav-header">{row_key}</li>
                        <li className="divider"></li>
                        {modalRows.map((row, idx) => {
                            return (
                                <li key={idx}>
                                    <a href="#" onClick={() => showModalOnRow(extension, row)}>
                                        {row[row_key]}
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
