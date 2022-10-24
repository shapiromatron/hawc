import _ from "lodash";
import { action, autorun, computed, observable } from "mobx";

import h from "shared/utils/helpers";
import Endpoint from "animal/Endpoint";
import { applyRecommendationLogic } from "bmd/common/recommendationLogic";

class Bmd3Store {
    constructor(config) {
        this.config = config;
    }
}

export default Bmd3Store;
