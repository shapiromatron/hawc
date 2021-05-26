import {observable, computed, action} from "mobx";

import h from "shared/utils/helpers";

class RobFormStore {
    // content
    @observable error = null;
    @observable config = null;
    @observable domains = null;

    // computed props
    @computed get dataLoaded() {
        return this.domains !== null;
    }

    // actions
    @action.bound setConfig(elementId) {
        this.config = JSON.parse(document.getElementById(elementId).textContent);
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

    // CRUD actions
    @action.bound cancelSubmitScores() {
        window.location.href = this.config.cancel_url;
    }
    @action.bound submitScores() {
        const payload = this.domains.map(d => [d.id, d.metrics.map(m => m.id)]),
            opts = h.fetchPost(this.config.csrf, payload, "PATCH"),
            url = this.config.submit_url;

        this.error = null;
        return fetch(url, opts)
            .then(response => {
                if (response.ok) {
                    window.location.href = this.config.cancel_url;
                } else {
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

const store = new RobFormStore();

// singleton pattern
export default store;
