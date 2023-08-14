import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component, useState} from "react";
import {ActionLink, ActionsButton} from "shared/components/ActionsButton";
import {markKeywords} from "shared/utils/_helpers";
import h from "shared/utils/helpers";
import Hero from "shared/utils/Hero";
import {getReferenceTagListUrl} from "shared/utils/urls";

import ReferenceButton from "./ReferenceButton";

class Reference extends Component {
    state = {abstractExpanded: false};
    toggleAbstract = () => {
        this.setState({ abstractExpanded: !this.state.abstractExpanded });
    };
    renderIdentifiers(data, study_url) {
        const nodes = [];

        if (data.full_text_url) {
            nodes.push(
                <a className="outline-btn mr-1 flex-shrink-0" href={data.full_text_url} key={h.randomString()}>
                    Full Text&nbsp;
                    <i className="fa fa-external-link" aria-hidden="true"></i>
                </a>
            );
        }

        _.chain(data.identifiers)
            .filter(v => v.url.length > 0)
            .sortBy(v => v.database_id)
            .each(v => {
                nodes.push(
                    <div className="d-flex mr-1 flex-shrink-0" key={h.randomString()}>
                        <a className="outline-btn left" href={v.database === "HERO" ? Hero.getUrl(v.id) : v.url}>
                            {v.database}    
                        </a>
                        <div className="outline-btn right" >
                            {v.id}
                        </div>
                    </div>
                );
            })
            .value();
        
        nodes.push(
            <div className="d-flex mr-1 flex-shrink-0" key={h.randomString()}>
                <a className="outline-btn left" href={data.url}>
                    <i className="fa fa-file-text" aria-hidden="true"></i>&nbsp;HAWC    
                </a>
                <div className="outline-btn right" style={data.has_study ? {borderRadius: "0px"} : null}>
                    {data.pk.toString()}
                </div>
                {data.has_study ? <a className="outline-btn right" href={study_url} key={h.randomString()}><i className="fa fa-book" aria-hidden="true"></i>&nbsp;Study</a> : null}
            </div>
        );

        if (data.searches.length) {
            nodes.push(
                <div
                    style={{minWidth: 85,}}
                    className={`dropdown outline-btn flex-shrink-0`}
                    key={h.randomString()}>
                    <a
                        className={`btn dropdown-toggle`}
                        data-toggle="dropdown"
                        aria-haspopup="true"
                        aria-expanded="false">
                        Imports&nbsp;
                        <i className="fa fa-search" aria-hidden="true"></i>
                    </a>
                    <div className="dropdown-menu dropdown-menu-right">
                        {data.searches.map((d, i) => (
                            <a className="dropdown-item" href={d.url}>{d.title}</a>
                        ))}
                    </div>
                </div>
                )
            }
        return <div className="d-flex my-1">{nodes}</div>;
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
                expanded,
            } = this.props,
            {data, tags} = reference,
            authors = !expanded ? (data.authors_short || data.authors || reference.NO_AUTHORS_TEXT) : (data.authors || data.authors_short || reference.NO_AUTHORS_TEXT),
            year = data.year || "",
            actionItems = [
                <ActionLink key={0} label="Edit reference tags" href={data.editTagUrl} />,
                <ActionLink key={1} label="Edit reference" href={data.editReferenceUrl} />,
                <ActionLink key={2} label="Delete reference" href={data.deleteReferenceUrl} />,
                <ActionLink key={3} label="Tag status" href={data.tagStatusUrl} />,
            ].concat(extraActions),
            {abstractExpanded} = this.state;

        return (
            <div className={expanded ? "referenceDetail expanded" : "referenceDetail"}>
                <div className="sticky-offset-anchor" id={`referenceId${data.pk}`}></div>
                {
                    <div className="d-flex ref_small">
                        <div>
                            <span title={expanded ? null : data.authors}>
                                {authors}&nbsp;{year}
                                {year != "" && data.journal && !expanded ? ". " : ""}
                                <i>{data.journal && !expanded ? data.journal : null}</i>
                            </span>
                            {data.title ? (
                            keywordDict ? (
                                <p
                                    style={{lineHeight: 1.25}}
                                    className="ref_title my-1"
                                    dangerouslySetInnerHTML={{
                                        __html: markKeywords(data.title, keywordDict),
                                    }}
                                />
                            ) : (
                                <p className="ref_title my-1">{data.title}</p>
                            )
                        ) : null}
                        {data.journal && expanded ? <p>{data.journal}</p> : null}
                    </div>
                        {showActionsTagless ? (
                            <ActionsButton
                                dropdownClasses={actionsBtnClassName}
                                items={actionItems.slice(1)}
                            />
                        ) : null}
                        {showActions ? (
                            <ActionsButton
                                dropdownClasses={actionsBtnClassName}
                                items={actionItems}
                            />
                        ) : null}
                    </div>
                }
                <div className="d-flex">
                    {this.renderIdentifiers(data, reference.get_study_url())}
                </div>
                {data.abstract ? (
                    <div
                        onClick={!expanded ? this.toggleAbstract : null}
                        className={abstractExpanded ? "abstracts" : "abstracts abstract-collapsed"}
                        style={expanded ? {} : {}}
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
                                style={{color: "white", }}
                                key={i}
                                href={getReferenceTagListUrl(data.assessment_id, tag.data.pk)}
                                className="refTag tagLink mt-1">
                                {tag.get_full_name()}
                            </a>
                        ))}
                    </p>
                ) : null}
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
    expanded: PropTypes.bool,
};

Reference.defaultProps = {
    showActions: false,
    actionsBtnClassName: "btn-sm btn-secondary",
    showHr: false,
    showTags: true,
    showActionsTagsless: false,
    extraActions: null,
    keywordDict: null,
    expanded: false,
};

export default Reference;
