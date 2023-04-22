import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionLink, ActionsButton} from "shared/components/ActionsButton";
import h from "shared/utils/helpers";
import Hero from "shared/utils/Hero";
import {getReferenceTagListUrl} from "shared/utils/urls";

import ReferenceButton from "./ReferenceButton";

const markKeywords = (text, allSettings) => {
        const all_tokens = allSettings.set1.keywords
                .concat(allSettings.set2.keywords)
                .concat(allSettings.set3.keywords),
            all_re = new RegExp(all_tokens.join("|"), "gim");

        if (all_tokens.length === 0) {
            return text;
        }
        text = text.replace(all_re, match => `<mark>${match}</mark>`);
        text = markText(text, allSettings.set1);
        text = markText(text, allSettings.set2);
        text = markText(text, allSettings.set3);
        return text;
    },
    markText = (text, settings) => {
        if (settings.keywords.length === 0) {
            return text;
        }
        const re = new RegExp(`<mark>(?<token>${settings.keywords.join("|")})</mark>`, "gim");
        return text.replace(
            re,
            (match, token) =>
                `<mark class="hawc-mk" title="${settings.name}" style='border-bottom: 1px solid ${settings.color}; box-shadow: inset 0 -4px 0 ${settings.color};'>${token}</mark>`
        );
    };

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
        const {
                reference,
                showActions,
                showTags,
                showHr,
                showActionsTagless,
                actionsBtnClassName,
                extraActions,
                keywordDict,
            } = this.props,
            {data, tags} = reference,
            authors = data.authors || data.authors_short || reference.NO_AUTHORS_TEXT,
            year = data.year || "",
            actionItems = [
                <ActionLink key={0} label="Edit reference tags" href={data.editTagUrl} />,
                <ActionLink key={1} label="Edit reference" href={data.editReferenceUrl} />,
                <ActionLink key={2} label="Delete reference" href={data.deleteReferenceUrl} />,
                <ActionLink key={3} label="Tag status" href={data.tagStatusUrl} />,
            ].concat(extraActions);

        return (
            <div className="referenceDetail pb-2">
                <div className="sticky-offset-anchor" id={`referenceId${data.pk}`}></div>
                {
                    <div className="ref_small">
                        {showActionsTagless ? (
                            <ActionsButton
                                dropdownClasses={actionsBtnClassName}
                                items={actionItems.slice(1)}
                            />
                        ) : null}
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
                {data.title ? (
                    keywordDict ? (
                        <p
                            className="ref_title py-1"
                            dangerouslySetInnerHTML={{
                                __html: markKeywords(data.title, keywordDict),
                            }}
                        />
                    ) : (
                        <p className="ref_title py-1">{data.title}</p>
                    )
                ) : null}
                {data.journal ? <p className="ref_small">{data.journal}</p> : null}
                {data.abstract ? (
                    <div
                        className="abstracts resize-y p-2"
                        style={data.abstract.length > 1500 ? {height: "45vh"} : null}
                        dangerouslySetInnerHTML={
                            keywordDict
                                ? {__html: markKeywords(data.abstract, keywordDict)}
                                : {__html: data.abstract}
                        }
                    />
                ) : null}
                {showTags && tags.length > 0 ? (
                    <p>
                        {tags.map((tag, i) => (
                            <a
                                style={{color: "white"}}
                                key={i}
                                href={getReferenceTagListUrl(data.assessment_id, tag.data.pk)}
                                className="refTag mt-1">
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
                        <strong>HAWC study details:&nbsp;</strong>
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
    showActionsTagless: PropTypes.bool,
    extraActions: PropTypes.arrayOf(PropTypes.element),
    keywordDict: PropTypes.object,
};

Reference.defaultProps = {
    showActions: false,
    actionsBtnClassName: "btn-sm",
    showHr: false,
    showTags: true,
    showActionsTagsless: false,
    extraActions: null,
    keywordDict: null,
};

export default Reference;
