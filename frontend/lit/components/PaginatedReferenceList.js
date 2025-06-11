import {action, computed, makeObservable, observable} from "mobx";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";
import Paginator from "shared/components/Paginator";
import h from "shared/utils/helpers";

import Reference from "../Reference";
import ReferenceTable from "./ReferenceTable";
import TagActions from "./TagActions";

class ReferenceListStore {
    @observable currentPage = null;
    @observable formattedReferences = null;

    constructor(settings) {
        makeObservable(this);
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
                this.formattedReferences = Reference.array(res.results, tag.tree);
            });
    }

    @action.bound fetchFirstPage() {
        let url = `/lit/api/assessment/${this.settings.assessment_id}/references/`,
            {search_id, required_tags, pruned_tags} = this.settings;
        url += `?tag_id=${this.settings.tag_id}`;
        if (search_id) {
            url += `&search_id=${search_id}`;
        }
        if (required_tags && required_tags.length > 0) {
            url += `&required_tags=${required_tags.join(",")}`;
        }
        if (pruned_tags && pruned_tags.length > 0) {
            url += `&pruned_tags=${pruned_tags.join(",")}`;
        }
        this.fetchPage(url);
    }
}

@observer
class PaginatedReferenceList extends Component {
    constructor(props) {
        makeObservable(this);
        super(props);
        this.store = new ReferenceListStore(props.settings);
    }
    componentDidMount() {
        this.store.fetchFirstPage();
    }
    render() {
        const {hasPage, formattedReferences, currentPage, fetchPage} = this.store,
            {settings, canEdit} = this.props;
        if (!hasPage) {
            return <Loading />;
        }
        return (
            <>
                <div className="d-flex">
                    <TagActions
                        assessmentId={settings.assessment_id}
                        tagId={settings.tag_id}
                        canEdit={canEdit}
                    />
                </div>
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
        required_tags: PropTypes.array.isRequired,
        pruned_tags: PropTypes.array.isRequired,
    }),
    canEdit: PropTypes.bool,
};
PaginatedReferenceList.defaultProps = {
    canEdit: false,
};

export default PaginatedReferenceList;
