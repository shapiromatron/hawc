import BaseStore from "./BaseStore";
import ExploratoryHeatmapStore from "./ExploratoryHeatmapStore";

class ExploratoryHeatmap {
    constructor(config) {
        this.base = new BaseStore(this, config);
        this.subclass = new ExploratoryHeatmapStore(this);
    }
}

const createExploratoryHeatmapStore = function (config) {
    return new ExploratoryHeatmap(config);
};

export {createExploratoryHeatmapStore};
