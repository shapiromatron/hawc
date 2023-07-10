import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
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
            items = _.sortedUniq(_.keys(this.props.store.intersection[widget.column]).sort()),
            _itemState = this.props.store._filterWidgetState[widget.column],
            itemState = this.props.store.filterWidgetState[widget.column],
            filterWidgetExtension = this.props.store.extensions.filterWidgets[widget.column],
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
                    className="p-1 pl-3"
                    style={{
                        backgroundColor: colorScale(maxValue),
                        color: h.getTextContrastColor(colorScale(maxValue)),
                        flex: 0,
                    }}>
                    <h4 className="m-0">{widgetTitle}</h4>
                </div>
                <div
                    style={{
                        overflowY: "auto",
                        flex: 1,
                    }}>
                    {items
                        .map((item, index) =>
                            this.renderItem(widget, item, index, _itemState, itemState, filterWidgetExtension)
                        )}
                </div>
            </div>
        );
    }

    renderItem(widget, item, index, _itemState, itemState, filterWidgetExtension) {
        const {toggleItemSelection, colorScale, maxValue} = this.props.store,
            {rows} = this.props.store.getTableData,
            itemRows = [...this.props.store.intersection[widget.column][item]],
            numItems = itemRows.filter(itemRow => rows.includes(itemRow)).length;
        return (
            <div key={index} className="my-1" style={{display:"flex",border: _itemState[item]?`1px solid ${colorScale(maxValue)}`:undefined}}>
                <label className="m-0 font-weight-normal" role="button" style={{flex:"1 1 auto"}}>
                    <input
                        className="hidden"
                        checked={_itemState[item]}
                        type="checkbox"
                        onChange={e => toggleItemSelection(widget.column, item, e.target.checked)}
                    />
                    <div style={{display:"flex"}}>
                        <div
                            className="mr-1"
                            style={{
                                flex:"0 0 2.5em",
                                display:"inline-flex",
                                justifyContent:"center",
                                alignItems:"center",
                                backgroundColor: colorScale(numItems),
                                color: h.getTextContrastColor(colorScale(numItems)),
                                height: "1.5em",
                            }}>
                            <span>{numItems}</span>
                        </div>
                        <div style={{flex:"1 1 auto",}}>{item == "" ? h.nullString : item}</div>
                    </div>
                </label>
                <span style={{flex:"0 0 min-content"}}>
                    {filterWidgetExtension && filterWidgetExtension.hasModal
                            ? this.renderButton(widget, item)
                            : null}
                </span>
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
