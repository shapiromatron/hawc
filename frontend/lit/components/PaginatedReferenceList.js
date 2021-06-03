import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";
import {observable, action, computed} from "mobx";

import h from "shared/utils/helpers";
import Loading from "shared/components/Loading";
import Paginator from "shared/components/Paginator";

import Reference from "../Reference";
import ReferenceTable from "./ReferenceTable";

class ReferenceListStore {
    @observable currentPage = null;
    @observable formattedReferences = null;

    constructor(settings) {
        this.settings = settings;
    }

    @computed get hasPage() {
        return this.currentPage !== null;
    }

    @action.bound fetchPage(url) {
        const {tag} = this.settings;
        fetch(url, h.fetchGet)
            .then(res => res.json())
            .then(res => {
                this.currentPage = res;
                let expected_references = new Set(tag.get_references_deep()),
                    refs = res.results
                        .map(datum => new Reference(datum, tag.tree))
                        .filter(ref => expected_references.has(ref.data.id));
                refs = Reference.sorted(refs);
                this.formattedReferences = refs;
            });
    }

    @action.bound fetchFirstPage() {
        let url = `/lit/api/assessment/${this.settings.assessment_id}/references/`;
        url += `?tag_id=${this.settings.tag_id}`;
        if (this.settings.search_id) {
            url += `&search_id=${this.settings.search_id}`;
        }
        this.fetchPage(url);
    }
}

@observer
class PaginatedReferenceList extends Component {
    constructor(props) {
        super(props);
        this.store = new ReferenceListStore(props.settings);
    }
    componentDidMount() {
        this.store.fetchFirstPage();
    }
    render() {
        const {hasPage, formattedReferences, currentPage, fetchPage} = this.store;
        if (!hasPage) {
            return <Loading />;
        }

        return (
            <>
                {formattedReferences ? (
                    <ReferenceTable references={formattedReferences} showActions={false} />
                ) : null}
                <Paginator page={currentPage} onChangePage={fetchPage} />
            </>
        );
    }
}

PaginatedReferenceList.propTypes = {
    settings: PropTypes.shape({
        assessment_id: PropTypes.number.isRequired,
        tag_id: PropTypes.number.isRequired,
        search_id: PropTypes.number,
        tag: PropTypes.object.isRequired,
    }),
};

export default PaginatedReferenceList;
