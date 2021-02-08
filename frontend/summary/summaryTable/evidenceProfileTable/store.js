import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

import {
    moveArrayElementUp,
    moveArrayElementDown,
    deleteArrayElement,
} from "shared/components/EditableRowData";

class EvidenceProfileTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable showCellModal = false;
    @observable stagedContent = null;
    @observable editErrorText = "";
    @observable showColumnEdit = false;
    @observable editTabIndex = 0;

    constructor(editMode, settings, editRootStore) {
        this.editMode = editMode;
        this.settings = settings;
        this.editRootStore = editRootStore;
        if (editMode && editRootStore) {
            autorun(() => {
                this.editRootStore.updateTableContent(JSON.stringify(this.settings), false);
            });
        }
    }

    @computed get numSummaryRows() {
        return (
            6 +
            Math.max(this.settings.exposed_human.cell_rows.length, 1) +
            Math.max(this.settings.animal.cell_rows.length, 1) +
            Math.max(this.settings.mechanistic.cell_rows.length, 1)
        );
    }
    @computed get numEpiJudgementRowSpan() {
        return this.settings.exposed_human.merge_judgement
            ? this.settings.exposed_human.cell_rows.length
            : 1;
    }
    @computed get numAniJudgementRowSpan() {
        return this.settings.animal.merge_judgement ? this.settings.animal.cell_rows.length : 1;
    }
    @computed get numMechJudgementRowSpan() {
        return this.settings.mechanistic.merge_judgement
            ? this.settings.mechanistic.cell_rows.length
            : 1;
    }

    @action.bound editTabIndexUpdate(editTabIndex) {
        this.editTabIndex = editTabIndex;
    }

    @action.bound createHumanRow() {
        const content = {
            summary: {
                findings: "<p>....</p>",
            },
            evidence: {
                evidence: "<p>....</p>",
                optional: "<p>...</p>",
                confidence: "<p>...</p>",
            },
            judgement: {
                judgement: 1,
                description: "<p>...</p>",
            },
            certain_factors: {
                factors: ["<p>...</p>", "<p>...</p>"],
            },
            uncertain_factors: {
                factors: ["<p>...</p>", "<p>...</p>"],
            },
        };
        this.settings.exposed_human.cell_rows.push(content);
    }
    @action.bound createAnimalRow() {
        const content = {
            summary: {
                findings: "<p>....</p>",
            },
            evidence: {
                evidence: "<p>....</p>",
                optional: "<p>...</p>",
                confidence: "<p>...</p>",
            },
            judgement: {
                judgement: 1,
                description: "<p>...</p>",
            },
            certain_factors: {
                factors: ["<p>...</p>", "<p>...</p>"],
            },
            uncertain_factors: {
                factors: ["<p>...</p>", "<p>...</p>"],
            },
        };
        this.settings.animal.cell_rows.push(content);
    }
    @action.bound createMechanisticRow() {
        const content = {
            summary: {
                findings: "<p>...</p>",
            },
            evidence: {
                description: "<p>...</p>",
            },
            judgement: {
                description: "<p>...</p>",
            },
        };
        this.settings.mechanistic.cell_rows.push(content);
    }

    @action.bound moveRowUp(content, index) {
        const arr = _.cloneDeep(this.settings[content].cell_rows);
        moveArrayElementUp(arr, index);
        this.settings[content].cell_rows = arr;
    }
    @action.bound moveRowDown(content, index) {
        const arr = _.cloneDeep(this.settings[content].cell_rows);
        moveArrayElementDown(arr, index);
        this.settings[content].cell_rows = arr;
    }
    @action.bound deleteRow(content, index) {
        const arr = _.cloneDeep(this.settings[content].cell_rows);
        deleteArrayElement(arr, index);
        this.settings[content].cell_rows = arr;
    }
    @action.bound updateValue(name, value) {
        _.set(this.settings, name, value);
    }

    // inject new settings from parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
}

export default EvidenceProfileTableStore;
