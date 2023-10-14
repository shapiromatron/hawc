import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

const NULL_VALUE = "---",
    EMPTY = {id: NULL_VALUE, label: NULL_VALUE},
    formatDataset = data => {
        // add 1-based __index__ attribute to each row; start at 2
        _.each(data, (row, index) => (row.__index__ = index + 2));
        // cast boolean fields to strings
        _.each(data, row =>
            _.each(row, (value, key) => {
                if (typeof value === "boolean") {
                    row[key] = value.toString();
                }
            })
        );
        return data;
    };

class Store {
    constructor(config) {
        this.config = config;
    }

    // 1. get assessment level metadata
    @observable references = null;
    @observable tags = null;
    @computed get hasAssessmentData() {
        // has input data been loaded?
        return _.isArray(this.references) && _.isArray(this.tags);
    }
    @action.bound fetchReferences() {
        const url = `/lit/api/assessment/${this.config.assessment_id}/reference-ids/`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => (this.references = json));
    }
    @action.bound fetchTags() {
        const url = `/lit/api/assessment/${this.config.assessment_id}/tags/`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => (this.tags = json));
    }

    // 2. upload xlsx file
    @observable dataset = NULL_VALUE;
    @computed get hasValidXlsx() {
        // do we have a parsable spreadsheet?
        return this.hasAssessmentData && _.isArray(this.dataset);
    }
    @action.bound handleFileInput(file) {
        const url = `/lit/api/assessment/${this.config.assessment_id}/excel-to-json/?format=json`,
            payload = h.fetchPostFile(this.config.csrf, file);
        fetch(url, payload)
            .then(response => response.json())
            .then(data => (this.dataset = formatDataset(data)));
    }
    @computed get datasetColumns() {
        return _.chain(this.dataset)
            .first()
            .keys()
            .filter(v => !v.startsWith("__"))
            .value();
    }
    @computed get datasetColumnChoices() {
        return _.chain(this.datasetColumns)
            .map(v => ({id: v, label: v}))
            .unshift(_.clone(EMPTY))
            .value();
    }
    get referenceColumnTypeChoices() {
        return [
            _.clone(EMPTY),
            {id: "reference_id", label: "HAWC"},
            {id: "hero_id", label: "HERO"},
            {id: "pubmed_id", label: "PubMed"},
            {id: "doi_id", label: "DOI"},
        ];
    }

    // 3. match hawc references to dataset
    @observable referenceIdColumn = NULL_VALUE;
    @observable referenceColumnType = NULL_VALUE;
    @computed get hasMatchingReferences() {
        // do we have at least one row where IDs match HAWC ids?
        return this.hasValidXlsx && this.matchedDatasetRows.length > 0;
    }
    @action.bound setReferenceIdColumn(col) {
        // xlsx column name for ids
        this.referenceIdColumn = col;
    }
    @action.bound setReferenceColumnType(col) {
        // xlsx reference id column type
        this.referenceColumnType = col;
    }
    @computed get numReferencesInHawc() {
        return this.references.length;
    }
    @computed get referenceMap() {
        // map of all references in hawc and their matches
        const colType = this.referenceColumnType,
            mapping = colType
                ? _.chain(this.references)
                      .filter(row => row[colType])
                      .map(row => [row[colType], row.reference_id])
                      .value()
                : [];
        return new Map(mapping);
    }
    @computed get matchedDatasetRows() {
        // filtered list of dataset rows
        const map = this.referenceMap,
            keyColumn = this.referenceIdColumn;
        return _.chain(this.dataset)
            .filter(row => map.has(row[keyColumn]))
            .value();
    }
    @computed get unmatchedDatasetRows() {
        // filtered list of dataset rows
        const map = this.referenceMap,
            keyColumn = this.referenceIdColumn;
        return _.chain(this.dataset)
            .filter(row => !map.has(row[keyColumn]))
            .value();
    }

    // 4. match metadata to hawc tags
    @observable datasetTagColumn = NULL_VALUE;
    @action.bound setDatasetTagColumn(col) {
        // column name in provided dataset for tags
        this.datasetTagColumn = col;
        this.resetSubmissionStatus();
    }

    @observable datasetTagValue = NULL_VALUE;
    @computed get datasetTagValueChoices() {
        const datasetTagColumn = this.datasetTagColumn;
        if (datasetTagColumn === NULL_VALUE) {
            return [];
        }
        return _.chain(this.dataset)
            .map(d => d[datasetTagColumn])
            .uniq()
            .map(v => ({id: v, label: v}))
            .unshift(_.clone(EMPTY))
            .value();
    }
    @computed get hasDatasetTagValue() {
        return this.datasetTagValue !== NULL_VALUE;
    }
    @action.bound setDatasetTagValue(value) {
        // column name in provided dataset for tags
        this.datasetTagValue = value;
        this.resetSubmissionStatus();
    }

    @computed get matchedRowsWithValue() {
        // rows with matched ids and value
        const column = this.datasetTagColumn,
            value = this.datasetTagValue,
            map = this.referenceMap,
            keyColumn = this.referenceIdColumn;
        if (column == NULL_VALUE || value == NULL_VALUE) {
            return [];
        }
        return this.matchedDatasetRows
            .filter(row => {
                return row[column] == value;
            })
            .map(row => {
                return {
                    __index__: row.__index__,
                    referenceKey: keyColumn,
                    referenceValue: row[keyColumn],
                    reference_id: map.get(row[keyColumn]),
                };
            });
    }
    @computed get unmatchedRowsWithValue() {
        // rows with unmatched ids and value
        const column = this.datasetTagColumn,
            value = this.datasetTagValue,
            keyColumn = this.referenceIdColumn;
        if (column == NULL_VALUE || value == NULL_VALUE) {
            return [];
        }
        return this.unmatchedDatasetRows
            .filter(row => {
                return row[column] == value;
            })
            .map(row => {
                return {
                    __index__: row.__index__,
                    referenceKey: keyColumn,
                    referenceValue: row[keyColumn],
                };
            });
    }

    @observable tag = NULL_VALUE;
    @computed get tagChoices() {
        return _.chain(this.tags)
            .map(v => ({id: v["id"], label: v["nested_name"].replaceAll("|", " ➤ ")}))
            .unshift(_.clone(EMPTY))
            .value();
    }
    @action.bound setTag(value) {
        // tag to apply
        this.tag = value;
        this.resetSubmissionStatus();
    }

    @observable tagVerb = "append";
    get tagVerbChoices() {
        return [
            {id: "append", label: "Apply"},
            {id: "remove", label: "Remove"},
        ];
    }
    @action.bound setTagVerb(value) {
        this.tagVerb = value;
        this.resetSubmissionStatus();
    }
    @computed get submissionData() {
        if (this.matchedRowsWithValue.length === 0) {
            return "";
        }
        const tag = this.tag,
            dataRows = this.matchedRowsWithValue
                .map(row => `${row.reference_id},${tag}`)
                .join("\n");
        return `reference_id,tag_id\n${dataRows}\n`;
    }
    @computed get canBeSubmitted() {
        return this.submissionData.length > 0 && this.tag !== NULL_VALUE;
    }
    @action.bound submitForm() {
        this.bulkUpdateTags();
    }
    @action.bound resetForm() {
        this.datasetTagColumn = NULL_VALUE;
        this.datasetTagValue = NULL_VALUE;
        this.tag = NULL_VALUE;
        this.tagVerb = "append";
        this.isSubmitting = false;
        this.submissionSuccessful = null;
    }

    @observable isSubmitting = false;
    @observable submissionSuccessful = null; // true/false/null
    @action.bound bulkUpdateTags() {
        let url = `/lit/api/assessment/${this.config.assessment_id}/reference-tags/`,
            payload = {operation: this.tagVerb, csv: this.submissionData};
        this.isSubmitting = true;
        this.submissionSuccessful = null;
        h.handleSubmit(
            url,
            "POST",
            this.config.csrf,
            payload,
            () => {
                this.submissionSuccessful = true;
                this.isSubmitting = false;
            },
            err => {
                this.submissionSuccessful = false;
                this.isSubmitting = false;
                console.error(err);
            },
            err => {
                this.submissionSuccessful = false;
                this.isSubmitting = false;
                console.error(err);
            }
        );
    }
    @action.bound resetSubmissionStatus() {
        this.isSubmitting = false;
        this.submissionSuccessful = null;
    }
}

export default Store;
