import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionLink, ActionsButton} from "shared/components/ActionsButton";

const getActionLinks = function(assessmentId, tagId, untagged, canEdit) {
    let links = [];
    if (untagged && canEdit) {
        links.push(
            <ActionLink
                key={0}
                label="Tag untagged references"
                href={`/lit/assessment/${assessmentId}/tag/untagged/`}
            />
        );
    }
    if (tagId) {
        links = [
            <ActionLink
                key={1}
                label="Download references"
                href={`/lit/api/tags/${tagId}/references/?format=xlsx`}
            />,
            <ActionLink
                key={2}
                label="Download references (table-builder format)"
                href={`/lit/api/tags/${tagId}/references/?format=xlsx&exporter=table-builder`}
            />,
        ];
        if (canEdit) {
            links.push(
                <ActionLink
                    key={3}
                    label="Tag references with this tag (but not descendants)"
                    href={`/lit/tag/${tagId}/tag/`}
                />
            );
        }
    }
    return links;
};

class TagActions extends Component {
    render() {
        const {assessmentId, tagId, untagged, canEdit} = this.props,
            links = getActionLinks(assessmentId, tagId, untagged, canEdit);
        if (links.length == 0) {
            return null;
        }
        return <ActionsButton containerClasses="btn-primary" items={links} />;
    }
}

TagActions.propTypes = {
    assessmentId: PropTypes.number.isRequired,
    tagId: PropTypes.number,
    untagged: PropTypes.bool.isRequired,
    canEdit: PropTypes.bool.isRequired,
};
TagActions.defaultProps = {
    untagged: false,
    canEdit: false,
};

export default TagActions;
