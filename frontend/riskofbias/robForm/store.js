import {observable, action} from "mobx";

class RobFormStore {
    @observable itemsLoaded = false;

    @action.bound fetchFullStudyIfNeeded() {}
    @action.bound submitRiskOfBiasScores() {}
    @action.bound scoreStateChange() {}
    @action.bound createScoreOverride() {}
    @action.bound deleteScoreOverride() {}
}

const store = new RobFormStore();

// singleton pattern
export default store;
