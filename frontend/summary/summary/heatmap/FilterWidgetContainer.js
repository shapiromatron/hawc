import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

@observer
class FilterWidget extends Component {
    constructor(props) {
        super(props);
        this.renderItem = this.renderItem.bind(this);
    }
    render() {
        const {widget} = this.props,
            items = _.keys(this.props.store.intersection[widget.column]),
            {selectAllFilterWidget, selectNoneFilterWidget} = this.props.store,
            itemStore = this.props.store.filterWidgetState[widget.column];

        return (
            <div className="well">
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
                <div className="clearfix"></div>
                <div>
                    {items
                        .sort()
                        .map((item, index) => this.renderItem(widget, item, index, itemStore))}
                </div>
            </div>
        );
    }
    renderItem(widget, item, index, itemStore) {
        const {toggleItemSelection, modal} = this.props.store;

        return (
            <div key={index}>
                <button
                    className="btn btn-mini pull-right"
                    onClick={() =>
                        modal
                            .addHeader(`<h4>${widget.column}: ${item}</h4>`)
                            .addFooter("")
                            .show()
                    }
                    title="View additional information">
                    <i className="icon-eye-open"></i>
                </button>
                <label className="checkbox">
                    <input
                        checked={itemStore[item]}
                        type="checkbox"
                        onChange={function(e) {
                            toggleItemSelection(widget.column, item, e.target.checked);
                        }}
                    />
                    <span>&nbsp;{item}</span>
                </label>
            </div>
        );
    }
}
FilterWidget.propTypes = {
    store: PropTypes.object,
    widget: PropTypes.object,
};

@observer
class FilterWidgetContainer extends Component {
    render() {
        const {store} = this.props,
            {filter_widgets} = this.props.store.settings;
        return (
            <div>
                {filter_widgets.map((widget, idx) => (
                    <FilterWidget key={idx} store={store} widget={widget} />
                ))}
            </div>
        );
    }
}
FilterWidgetContainer.propTypes = {
    store: PropTypes.object,
};

export default FilterWidgetContainer;
