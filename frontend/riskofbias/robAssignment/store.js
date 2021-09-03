import * as d3 from "d3";
import _ from "lodash";
import {action, computed, observable} from "mobx";

import StudyRobStore from "../stores/StudyRobStore";

class RobAssignmentStore extends StudyRobStore {
    constructor(config) {
        super();
        this.config = config;
    }
}

export default RobAssignmentStore;
