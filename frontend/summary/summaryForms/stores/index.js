import BaseStore from "./BaseStore";
import ExploratoryHeatmapStore from "./ExploratoryHeatmapStore";

class ExploratoryHeatmap {
    constructor() {
        this.base = new BaseStore(this);
        this.subclass = new ExploratoryHeatmapStore(this);
    }
}

const createExploratoryHeatmapStore = function() {
    return new ExploratoryHeatmap();
};

export {createExploratoryHeatmapStore};
