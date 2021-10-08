import _ from "lodash";
import {action, computed, observable} from "mobx";

import h from "shared/utils/helpers";

import {deleteArrayElement} from "shared/components/EditableRowData";

class Store {
    config = null;
    @observable dataset = null;

    @observable references = null;
    @observable tags = null;

    @observable datasetIdColumn = null;
    @observable referenceIdColumn = null;
    @observable datasetTagColumn = null;

    @observable datasetTags = [];

    constructor(config) {
        this.config = config;
    }

    @action.bound handleFileInput(e) {
        fetch(`/lit/api/assessment/${this.config.assessment_id}/excel-to-json/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Disposition": "attachment; filename=upload",
                "X-CSRFToken": this.config.csrf,
            },
            body: e.target.files[0],
        })
            .then(response => response.json())
            .then(json => (this.dataset = json));
        return;
    }

    @action.bound getReferences() {
        fetch(`/lit/api/assessment/${this.config.assessment_id}/reference-ids/`, h.fetchGet)
            .then(response => response.json())
            .then(json => (this.references = json));
    }

    @action.bound getTags() {
        fetch(`/lit/api/assessment/${this.config.assessment_id}/tags/`, h.fetchGet)
            .then(response => response.json())
            .then(json => (this.tags = json));
    }

    @action.bound setDatasetIdColumn(col) {
        // column name in provided dataset for ids
        this.datasetIdColumn = col;
    }

    @action.bound setReferenceIdColumn(col) {
        // column name in returned references for ids
        // either reference_id, hero_id, or pubmed_id
        this.referenceIdColumn = col;
    }

    @action.bound setDatasetTagColumn(col) {
        // column name in provided dataset for tags
        this.datasetTagColumn = col;
        this.datasetTags = [];
    }

    @computed get datasetColumnChoices() {
        return _.chain(this.dataset)
            .first()
            .keys()
            .map(v => [v, v])
            .value();
    }

    get referenceColumnChoices() {
        return [
            ["reference_id", "HAWC ID"],
            ["hero_id", "HERO ID"],
            ["pubmed_id", "PUBMED ID"],
        ];
    }

    @computed get datasetTagChoices() {
        let tags = _.map(this.dataset, v => v[this.datasetTagColumn]),
            uniqueTags = [...new Set(tags)];
        return _.map(uniqueTags, v => [v, v]);
    }

    @computed get HAWCTagChoices() {
        return _.map(this.tags, v => [v["id"], v["nested_name"]]);
    }

    @action.bound createDatasetTag() {
        this.datasetTags.push({});
    }

    @action.bound deleteDatasetTag(index) {
        deleteArrayElement(this.datasetTags, index);
    }

    @action.bound setDatasetTagLabel(index, label) {
        // set the dataset tag label
        this.datasetTags[index].label = label;
    }

    @action.bound setDatasetTagId(index, id) {
        // set the tag id
        // since this is taken from user input, we have to parse the string to int
        this.datasetTags[index].id = parseInt(id);
    }

    @computed get referenceMap() {
        let ids = _.map(this.dataset, v => v[this.datasetIdColumn]),
            matchingReferences = _.chain(this.references)
                .filter(v => _.includes(ids, v[this.referenceIdColumn]))
                .map(v => [v[this.referenceIdColumn], v.reference_id])
                .value();
        return new Map(matchingReferences);
    }

    @computed get tagMap() {
        let tags = _.chain(this.datasetTags)
            .filter(v => !_.isNil(v.label) && !_.isNil(v.id))
            .map(v => [v.label, v.id])
            .value();
        return new Map(tags);
    }

    @computed get datasetFinal() {
        // creates a list of objects with reference_id and tag_id
        // string casts are done since input is string on datasetTags and thus tagMap
        let ids = [...this.referenceMap.keys()],
            tags = [...this.tagMap.keys()],
            foobar = _.chain(this.dataset)
                .filter(v => _.includes(ids, v[this.datasetIdColumn]))
                .filter(v => _.includes(tags, String(v[this.datasetTagColumn])))
                .map(v => ({
                    reference_id: this.referenceMap.get(v[this.datasetIdColumn]),
                    tag_id: this.tagMap.get(String(v[this.datasetTagColumn])),
                }))
                .value();
        return foobar;
    }

    @action.bound bulkUpdateTags() {
        let csv = h.objArrayToCSV(this.datasetFinal),
            payload = {operation: "append", csv};
        fetch(
            `/lit/api/assessment/${this.config.assessment_id}/reference-tags/`,
            h.fetchPost(this.config.csrf, payload, "POST")
        );
    }
}

export default Store;
