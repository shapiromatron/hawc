import BaseStore from "./Base";
import ExploratoryHeatmap from "./ExploratoryHeatmap";

class ExploratoryHeatmapStore {
    constructor() {
        this.base = new BaseStore(this);
        this.subclass = new ExploratoryHeatmap(this);
    }
}

const createExploratoryHeatmapStore = function() {
    return new ExploratoryHeatmapStore();
};

export {createExploratoryHeatmapStore};
