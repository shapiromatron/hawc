import BaseStore from "./BaseStore";
import CrossviewStore from "./CrossviewStore";
import ExploratoryHeatmapStore from "./ExploratoryHeatmapStore";
import PrismaStore from "./PrismaStore";
import RobStore from "./RobStore";

class ExploratoryHeatmap {
    constructor(config, djangoForm) {
        this.base = new BaseStore(this, config);
        this.subclass = new ExploratoryHeatmapStore(this);
        this.base.setDjangoForm(djangoForm);
        this.base.setInitialData();
    }
}

class Prisma {
    constructor(config, djangoForm) {
        this.base = new BaseStore(this, config);
        this.subclass = new PrismaStore(this);
        this.base.setDjangoForm(djangoForm);
        this.base.setInitialData();
    }
}

class Rob {
    constructor(config, djangoForm) {
        this.base = new BaseStore(this, config);
        this.subclass = new RobStore(this);
        this.base.setDjangoForm(djangoForm);
        this.base.setInitialData();
    }
}

class Crossview {
    constructor(config, djangoForm) {
        this.base = new BaseStore(this, config);
        this.subclass = new CrossviewStore(this);
        this.base.setDjangoForm(djangoForm);
        this.base.setInitialData();
    }
}

export const createExploratoryHeatmapStore = (config, djangoForm) =>
        new ExploratoryHeatmap(config, djangoForm),
    createPrismaStore = (config, djangoForm) => new Prisma(config, djangoForm),
    createRobStore = (config, djangoForm) => new Rob(config, djangoForm),
    createCrossviewStore = (config, djangoForm) => new Crossview(config, djangoForm);
