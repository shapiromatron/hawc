import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import {ActionLink, ActionsButton} from "shared/components/ActionsButton";
import h from "shared/utils/helpers";
import {getReferenceTagListUrl} from "shared/utils/urls";
import Hero from "shared/utils/Hero";

import ReferenceButton from "./ReferenceButton";

class Reference extends Component {
    renderIdentifiers(data) {
        const nodes = [];

        if (data.full_text_url) {
            nodes.push(
                <ReferenceButton
                    key={h.randomString()}
                    className={"btn btn-sm btn-primary"}
                    url={data.full_text_url}
                    displayText={"Full text link"}
                    textToCopy={data.full_text_url}
                />
            );
        }

        _.chain(data.identifiers)
            .filter(v => v.url.length > 0)
            .sortBy(v => v.database_id)
            .each(v => {
                nodes.push(
                    <ReferenceButton
                        key={h.randomString()}
                        className={"btn btn-sm btn-success"}
                        url={v.database === "HERO" ? Hero.getUrl(v.id) : v.url}
                        displayText={v.database}
                        textToCopy={v.id}
                    />
                );
            })
            .value();

        nodes.push(
            <ReferenceButton
                key={h.randomString()}
                className={"btn btn-sm btn-warning"}
                url={data.url}
                displayText={"HAWC"}
                textToCopy={data.pk.toString()}
            />
        );

        _.chain(data.identifiers)
            .reject(v => v.url.length > 0 || v.database === "External link")
            .sortBy(v => v.database_id)
            .each(v => {
                nodes.push(
                    <ReferenceButton
                        key={h.randomString()}
                        className={"btn btn-sm btn-secondary"}
                        url={v.url}
                        displayText={v.database}
                        textToCopy={v.id}
                    />
                );
            })
            .value();

        return <div>{nodes}</div>;
    }

    render() {
        const {reference, showActions, showTags, showHr, actionsBtnClassName} = this.props,
            {data, tags} = reference,
            authors = data.authors || data.authors_short || reference.NO_AUTHORS_TEXT,
            year = data.year || "",
            actionItems = [
                <ActionLink key={0} label="Edit tags" href={data.editTagUrl} />,
                <ActionLink key={1} label="Edit reference" href={data.editReferenceUrl} />,
                <ActionLink key={2} label="Delete reference" href={data.deleteReferenceUrl} />,
            ];

        return (
            <div className="referenceDetail">
                <div className="sticky-offset-anchor" id={`referenceId${data.pk}`}></div>
                {
                    <div className="ref_small">
                        <span>
                            {authors}&nbsp;{year}
                        </span>
                        {showActions ? (
                            <ActionsButton
                                dropdownClasses={actionsBtnClassName}
                                items={actionItems}
                            />
                        ) : null}
                    </div>
                }
                {data.title ? <p className="ref_title">{data.title}</p> : null}
                {data.journal ? <p className="ref_small">{data.journal}</p> : null}
                {data.abstract ? (
                    <div className="abstracts" dangerouslySetInnerHTML={{__html: data.abstract}} />
                ) : null}
                {showTags && tags.length > 0 ? (
                    <p>
                        {tags.map((tag, i) => (
                            <a
                                key={i}
                                href={getReferenceTagListUrl(data.assessment_id, tag.data.pk)}
                                className="referenceTag badge badge-info mr-1">
                                {tag.get_full_name()}
                            </a>
                        ))}
                    </p>
                ) : null}
                {data.searches.length > 0 ? (
                    <p className="my-1">
                        <strong>HAWC searches/imports:</strong>
                        {data.searches.map((d, i) => (
                            <span className="badge badge-light mr-1" key={i}>
                                &nbsp;<a href={d.url}>{d.title}</a>
                            </span>
                        ))}
                    </p>
                ) : null}
                {data.has_study ? (
                    <p className="my-1">
                        <strong>HAWC study extraction:&nbsp;</strong>
                        <a href={reference.get_study_url()}>{data.study_short_citation}</a>
                    </p>
                ) : null}
                {this.renderIdentifiers(data)}
                {showHr ? <hr /> : null}
            </div>
        );
    }
}

Reference.propTypes = {
    reference: PropTypes.object,
    showActions: PropTypes.bool,
    actionsBtnClassName: PropTypes.string,
    showHr: PropTypes.bool,
    showTags: PropTypes.bool,
};

Reference.defaultProps = {
    showActions: false,
    actionsBtnClassName: "btn-sm",
    showHr: false,
    showTags: true,
};

export default Reference;
