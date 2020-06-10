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
            <div className="container-fluid exp_heatmap_container">
                <h4>{widget.column}</h4>
                <div className="btn-group">
                    <button className="btn" onClick={() => selectAllFilterWidget(widget.column)}>
                        All
                    </button>
                    <button className="btn" onClick={() => selectNoneFilterWidget(widget.column)}>
                        None
                    </button>
                </div>
                <div>
                    {items.map((item, index) => this.renderItem(widget, item, index, itemStore))}
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
                    }>
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
