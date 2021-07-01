import React from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";
import {observable, action} from "mobx";

import h from "shared/utils/helpers";

class DescriptionStore {
    // Create a universal toggle to show/hide metric descriptions
    @observable show = false;
    @action.bound toggle = () => (this.show = !this.show);
}
const store = new DescriptionStore(); // singleton store; shared across all components

const MetricDescription = observer(props => {
    if (!store.show) {
        return null;
    }
    return <div dangerouslySetInnerHTML={{__html: props.html}} />;
});

@observer
class MetricToggle extends React.Component {
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

MetricDescription.propTypes = {
    html: PropTypes.string.isRequired,
};
MetricToggle.propTypes = {
    initiallyShow: PropTypes.bool,
};

export {MetricToggle, MetricDescription};
