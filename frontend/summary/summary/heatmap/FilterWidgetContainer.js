import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

import {getAction, showAsModal} from "../../interactivity/actions";

@observer
class FilterWidget extends Component {
    constructor(props) {
        super(props);
        this.renderItem = this.renderItem.bind(this);
    }
    render() {
        const {widget, numWidgets} = this.props,
            {colorScale, maxValue} = this.props.store,
            {rows} = this.props.store.getTableData,
            maxHeight = `${Math.floor((1 / numWidgets) * 100)}vh`,
            _itemState = this.props.store._filterWidgetState[widget.column],
            allItems = _.keys(this.props.store.intersection[widget.column]),
            items = _.sortedUniq(
                (_.some(_.values(_itemState))
                    ? allItems
                    : allItems.filter(item => {
                          let itemRows = [...this.props.store.intersection[widget.column][item]];
                          for (let itemRow of itemRows) {
                              if (rows.includes(itemRow)) {
                                  return true;
                              }
                          }
                          return false;
                      })
                ).sort()
            ),
            action = getAction(widget.on_click_event),
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
                    {items.map((item, index) =>
                        this.renderItem(widget, item, index, _itemState, action)
                    )}
                </div>
            </div>
        );
    }

    renderItem(widget, item, index, _itemState, action) {
        const {toggleItemSelection, colorScale, maxValue, settings} = this.props.store,
            {rows} = this.props.store.getTableData,
            itemRows = [...this.props.store.intersection[widget.column][item]],
            numItems = itemRows.filter(itemRow => rows.includes(itemRow)).length,
            isSelected = _itemState[item],
            showCounts = settings.show_counts;
        return (
            <div
                key={index}
                className="my-1"
                style={{
                    display: "flex",
                    outline: isSelected ? `2px solid ${colorScale(maxValue)}` : undefined,
                    outlineOffset: isSelected ? "-2px" : undefined,
                    backgroundColor: isSelected ? colorScale(maxValue * 0.1) : undefined,
                }}>
                <label className="m-0 font-weight-normal" role="button" style={{flex: "1 1 auto"}}>
                    <input
                        className="hidden"
                        checked={isSelected}
                        type="checkbox"
                        onChange={e => toggleItemSelection(widget.column, item, e.target.checked)}
                    />
                    <div style={{display: "flex"}}>
                        <div
                            className="mr-1"
                            style={{
                                flex: "0 0 2.5em",
                                display: "inline-flex",
                                justifyContent: "center",
                                alignItems: "center",
                                backgroundColor: colorScale(numItems),
                                color: h.getTextContrastColor(colorScale(numItems)),
                                height: "1.5em",
                            }}>
                            {showCounts ? <span>{numItems}</span> : null}
                        </div>
                        <div style={{flex: "1 1 auto"}}>{item == "" ? h.nullString : item}</div>
                    </div>
                </label>
                <span style={{flex: "0 0 min-content"}}>
                    {action && action.modal ? this.renderButton(widget, item, action) : null}
                </span>
            </div>
        );
    }

    renderButton(widget, item, action) {
        const matched = _.chain(this.props.store.getTableData.data)
            .filter(d => d[widget.column] == item)
            .value();

        // cycle through columns to see if there's a single item in a column
        for (let column of action.columns) {
            const items = _.chain(matched)
                .uniqBy(column)
                .sortBy(column)
                .value();

            // only show button if there's a single item
            if (items.length === 1) {
                return (
                    <button
                        className="btn btn-sm"
                        onClick={e => {
                            e.stopPropagation();
                            showAsModal(action, items[0]);
                        }}
                        title="View additional information">
                        <i className="fa fa-fw fa-external-link"></i>
                    </button>
                );
            }
        }

        // couldn't find a column with a single item; show hidden to preserve layout
        return (
            <button className="btn btn-sm disabled" title="Disabled">
                <i className="fa fa-fw"></i>
            </button>
        );
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
