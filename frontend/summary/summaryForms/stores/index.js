import BaseStore from "./BaseStore";
import ExploratoryHeatmapStore from "./ExploratoryHeatmapStore";
import PrismaStore from "./PrismaStore";
import RobStore from "./RobStore";

class ExploratoryHeatmap {
    constructor(config) {
        this.base = new BaseStore(this, config);
        this.subclass = new ExploratoryHeatmapStore(this);
    }
}

class Prisma {
    constructor(config) {
        this.base = new BaseStore(this, config);
        this.subclass = new PrismaStore(this);
    }
}

class Rob {
    constructor(config) {
        this.base = new BaseStore(this, config);
        this.subclass = new RobStore(this);
    }
}

export const createExploratoryHeatmapStore = function(config) {
        return new ExploratoryHeatmap(config);
    },
    createPrismaStore = function(config) {
        return new Prisma(config);
    },
    createRobStore = function(config) {
        return new Rob(config);
    };
