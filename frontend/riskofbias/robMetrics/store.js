import {action, computed, makeObservable, observable} from "mobx";
import h from "shared/utils/helpers";

class RobMetricsStore {
    constructor(config) {
        makeObservable(this);
        this.config = config;
    }

    // content
    @observable error = null;
    @observable domains = null;

    // computed props
    @computed get dataLoaded() {
        return this.domains !== null;
    }

    @computed get isEditing() {
        return this.config.is_editing;
    }

    @action.bound fetchRoBData() {
        fetch(this.config.api_url)
            .then(resp => resp.json())
            .then(json => {
                this.domains = json;
            })
            .catch(exception => {
                this.error = exception;
            });
    }

    @action.bound moveMetric(domainIndex, metricIndex, down) {
        let domain = this.domains[domainIndex];
        if (down) {
            if (metricIndex === domain.metrics.length - 1) {
                return;
            }
            domain.metrics.splice(metricIndex + 1, 0, domain.metrics.splice(metricIndex, 1)[0]);
        } else {
            if (metricIndex === 0) {
                return;
            }
            domain.metrics.splice(metricIndex - 1, 0, domain.metrics.splice(metricIndex, 1)[0]);
        }
        this.submitSort();
    }

    @action.bound moveDomain(domainIndex, down) {
        if (down) {
            if (domainIndex === this.domains.length - 1) {
                return;
            }
            this.domains.splice(domainIndex + 1, 0, this.domains.splice(domainIndex, 1)[0]);
        } else {
            if (domainIndex === 0) {
                return;
            }
            this.domains.splice(domainIndex - 1, 0, this.domains.splice(domainIndex, 1)[0]);
        }
        this.submitSort();
    }

    // CRUD actions
    @action.bound submitSort() {
        const payload = this.domains.map(d => [d.id, d.metrics.map(m => m.id)]),
            opts = h.fetchPost(this.config.csrf, payload, "PATCH"),
            url = this.config.submit_url;

        this.error = null;
        return fetch(url, opts)
            .then(response => {
                if (!response.ok) {
                    response.text().then(text => {
                        this.error = text;
                    });
                }
            })
            .catch(error => {
                this.error = error;
            });
    }
}

export default RobMetricsStore;
