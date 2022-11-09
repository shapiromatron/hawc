import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";
import ExploreHeatmap from "summary/summary/ExploreHeatmap";

@inject("store")
@observer
class VisualTab extends Component {
    updatePlot() {
        const {settingsHash, dataset, setDataset, settings} = this.props.store,
            el = document.getElementById(settingsHash),
            thisDataset = dataset && dataset.length > 0 ? dataset : undefined;
        if (el) {
            new ExploreHeatmap({settings}, thisDataset).displayAsPage($(el), {
                cb: self => {
                    setDataset(self.dataset);
                },
            });
        }
    }
    componentDidMount() {
        this.updatePlot();
    }
    componentDidUpdate() {
        this.updatePlot();
    }
    render() {
        const {settingsHash} = this.props.store;
        return (
            <div id={settingsHash}>
                <Loading />
            </div>
        );
    }
}
VisualTab.propTypes = {
    store: PropTypes.object,
};
export default VisualTab;
