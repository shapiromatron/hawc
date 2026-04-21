import _ from "lodash";
import {action, autorun, computed, makeObservable, observable} from "mobx";
import {
    deleteArrayElement,
    moveArrayElementDown,
    moveArrayElementUp,
} from "shared/components/EditableRowData";

const getDefaultEvidence = () => {
        const blank = "<p></p>";
        return {
            summary: {findings: blank},
            evidence: {description: blank},
            judgement: {
                judgement: 1,
                description: blank,
                custom_judgement_icon: "",
                custom_judgement_label: "",
            },
            certain_factors: {factors: [], text: blank},
            uncertain_factors: {factors: [], text: blank},
        };
    },
    getDefaultMechanisticEvidence = () => {
        const blank = "<p></p>";
        return {
            summary: {findings: blank},
            evidence: {description: blank},
            judgement: {description: blank},
        };
    };

class EvidenceProfileTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable showCellModal = false;
    @observable stagedContent = null;
    @observable editErrorText = "";
    @observable showColumnEdit = false;
    @observable editTabIndex = 0;

    constructor(editMode, table, editRootStore) {
        makeObservable(this);
        this.editMode = editMode;
        this.table = table;
        this.settings = table.content;
        this.editRootStore = editRootStore;
        if (editMode && editRootStore) {
            autorun(() => {
                this.editRootStore.updateTableContent(JSON.stringify(this.settings), false);
            });
        }
    }

    @computed get numSummaryRows() {
        let hide_exposed_human = this.settings.exposed_human.hide_content,
            hide_animal = this.settings.animal.hide_content,
            hide_mechanistic = this.settings.mechanistic.hide_content;

        let rows = 0;
        rows += hide_exposed_human && hide_animal ? 0 : 1;
        rows += hide_exposed_human ? 0 : 1 + Math.max(this.settings.exposed_human.rows.length, 1);
        rows += hide_animal ? 0 : 1 + Math.max(this.settings.animal.rows.length, 1);
        rows += hide_mechanistic ? 0 : 2 + Math.max(this.settings.mechanistic.rows.length, 1);

        return rows ? rows : 1;
    }
    @computed get numEpiJudgementRowSpan() {
        return this.settings.exposed_human.merge_judgement
            ? this.settings.exposed_human.rows.length
            : 1;
    }
    @computed get numAniJudgementRowSpan() {
        return this.settings.animal.merge_judgement ? this.settings.animal.rows.length : 1;
    }
    @computed get numMechJudgementRowSpan() {
        return this.settings.mechanistic.merge_judgement
            ? this.settings.mechanistic.rows.length
            : 1;
    }

    @action.bound editTabIndexUpdate(editTabIndex) {
        this.editTabIndex = editTabIndex;
    }

    @action.bound createHumanRow() {
        this.settings.exposed_human.rows.push(getDefaultEvidence());
    }
    @action.bound createAnimalRow() {
        this.settings.animal.rows.push(getDefaultEvidence());
    }
    @action.bound createMechanisticRow() {
        this.settings.mechanistic.rows.push(getDefaultMechanisticEvidence());
    }

    @action.bound toggleFactor(objectKey, factorKey) {
        let factors = _.cloneDeep(_.get(this.settings, objectKey).factors),
            index = _.findIndex(factors, d => d.key == factorKey);
        if (index >= 0) {
            factors.splice(index, 1);
        } else {
            factors.push({key: factorKey, short_description: "", long_description: ""});
        }

        factors = _.sortBy(factors, d => d.key);
        _.set(this.settings, `${objectKey}.factors`, factors);
    }

    @action.bound moveRowUp(content, index) {
        const arr = _.cloneDeep(this.settings[content].rows);
        moveArrayElementUp(arr, index);
        this.settings[content].rows = arr;
    }
    @action.bound moveRowDown(content, index) {
        const arr = _.cloneDeep(this.settings[content].rows);
        moveArrayElementDown(arr, index);
        this.settings[content].rows = arr;
    }
    @action.bound deleteRow(content, index) {
        const arr = _.cloneDeep(this.settings[content].rows);
        deleteArrayElement(arr, index);
        this.settings[content].rows = arr;
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
