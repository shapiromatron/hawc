import BaseStore from "./BaseStore";
import ExploratoryHeatmapStore from "./ExploratoryHeatmapStore";
import PrismaStore from "./PrismaStore";

class ExploratoryHeatmap {
    constructor(config) {
        this.base = new BaseStore(this, config);
        this.subclass = new ExploratoryHeatmapStore(this);
    }
}

class Prisma {
    constructor(config) {
        this.base = new BaseStore(this, config);
        this.subclass = new PrismaStore(this, config.prisma_data);
    }
}

export const createExploratoryHeatmapStore = function(config) {
        return new ExploratoryHeatmap(config);
    },
    createPrismaStore = function(config) {
        return new Prisma(config);
    };
