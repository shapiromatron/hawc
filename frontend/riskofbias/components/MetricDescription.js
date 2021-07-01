import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";
import {observable, action} from "mobx";

import h from "shared/utils/helpers";

class DescriptionStore {
    // A global toggle to show/hide metric descriptions
    @observable show = false;
    @action.bound toggle = () => (this.show = !this.show);
}

// singleton store; shared across all components
const store = new DescriptionStore();

@observer
class MetricToggle extends Component {
    render() {
        return (
            <button
                type="button"
                title="Show/hide description"
                className="pull-right btn btn-sm btn-light"
                onClick={() => {
                    store.toggle();
                    h.maybeScrollIntoView(this, {yOffset: -50, animate: true});
                }}>
                <i className={store.show ? "fa fa-fw fa-eye-slash" : "fa fa-fw fa-eye"}></i>
                &nbsp;{store.show ? "Hide details" : "Show details"}
            </button>
        );
    }
}
MetricToggle.propTypes = {
    initiallyShow: PropTypes.bool,
};

@observer
class MetricDescription extends Component {
    render() {
        if (!store.show) {
            return null;
        }
        return <div dangerouslySetInnerHTML={{__html: this.props.html}} />;
    }
}
MetricDescription.propTypes = {
    html: PropTypes.string.isRequired,
};

@observer
class MetricHeader extends Component {
    render() {
        const {metric} = this.props;
        return (
            <>
                <h4>
                    {metric.name}
                    <MetricToggle />
                </h4>
                <MetricDescription html={metric.description} />
            </>
        );
    }
}
MetricHeader.propTypes = {
    metric: PropTypes.object.isRequired,
};

export default MetricHeader;
