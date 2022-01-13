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
            {rows} = this.props.store.getTableData,
            allItems = _.keys(this.props.store.intersection[widget.column]),
            availableItems = allItems.filter(item => {
                let itemRows = [...this.props.store.intersection[widget.column][item]];
                for (let itemRow of itemRows) {
                    if (rows.includes(itemRow)) {
                        return true;
                    }
                }
                return false;
            }),
            itemStore = this.props.store.filterWidgetState[widget.column],
            hiddenItems = _.chain(itemStore)
                .keys()
                .filter(d => itemStore[d] === false)
                .value(),
            filterWidgetExtension = this.props.store.extensions.filterWidgets[widget.column],
            items = _.sortedUniq([...availableItems, ...hiddenItems].sort()),
            widgetTitle = widget.header ? widget.header : h.titleCase(widget.column);

        return (
            <div
                className="pb-2"
                style={{
                    minHeight: "100px",
                    maxHeight,
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                }}>
                <div
                    className="mb-1 p-1 pl-3"
                    style={{
                        backgroundColor: colorScale(maxValue),
                        color: h.getTextContrastColor(colorScale(maxValue)),
                        flex: 0,
                    }}>
                    <div className="btn-group float-right">
                        <button
                            className="btn btn-sm text-white"
                            onClick={() => selectAllFilterWidget(widget.column)}
                            title="Select all items">
                            <i className="fa fa-lg fa-check-circle"></i>
                        </button>
                        <button
                            className="btn btn-sm text-white"
                            onClick={() => selectNoneFilterWidget(widget.column)}
                            title="De-select all items">
                            <i className="fa fa-lg fa-times-circle"></i>
                        </button>
                    </div>
                    <h4 className="m-0">{widgetTitle}</h4>
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
            {rows} = this.props.store.getTableData,
            itemRows = [...this.props.store.intersection[widget.column][item]],
            numItems = itemRows.filter(itemRow => rows.includes(itemRow)).length;
        return (
            <div key={index}>
                <label className="form-check font-weight-normal" role="button">
                    <input
                        checked={itemStore[item]}
                        type="checkbox"
                        onChange={e => toggleItemSelection(widget.column, item, e.target.checked)}
                    />
                    <div
                        className="mx-1"
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
                    <span>{item == "" ? h.nullString : item}</span>
                    {filterWidgetExtension && filterWidgetExtension.hasModal
                        ? this.renderButton(widget, item)
                        : null}
                </label>
            </div>
        );
    }

    renderButton(widget, item) {
        const extensions = this.props.store.extensions.filterWidgets,
            {showModalOnRow} = this.props.store,
            extension = extensions[widget.column],
            row_key = extension._dpe_key,
            modalRows = _.chain(this.props.store.getTableData.data)
                .filter({
                    [widget.column]: item,
                })
                .uniqBy(row_key)
                .sortBy(row_key)
                .value();

        // If there are no results disable button
        if (modalRows.length == 0) {
            return (
                <button
                    className="btn btn-sm float-right py-0 disabled"
                    title="No additional information">
                    <i className="fa fa-eye-slash"></i>
                </button>
            );
        }

        // If there is one result link it to the button
        else if (modalRows.length == 1) {
            return (
                <button
                    className="btn btn-sm float-right py-0"
                    onClick={e => {
                        e.stopPropagation();
                        showModalOnRow(extension, modalRows[0]);
                    }}
                    title="View additional information">
                    <i className="fa fa-eye"></i>
                </button>
            );
        }

        // If there are too many results disable button
        else {
            return (
                <button className="btn btn-sm float-right py-0 disabled" title="Too many results">
                    <i className="fa fa-eye"></i>
                </button>
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
