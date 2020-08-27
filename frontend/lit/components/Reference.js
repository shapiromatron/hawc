import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import ReferenceButton from "./ReferenceButton";

class Reference extends Component {
    renderIdentifiers(data) {
        const nodes = [];

        if (data.full_text_url) {
            nodes.push(
                <ReferenceButton
                    key={h.randomString()}
                    className={"btn btn-mini btn-primary"}
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
                        className={"btn btn-mini btn-success"}
                        url={v.url}
                        displayText={v.database}
                        textToCopy={v.id}
                    />
                );
            })
            .value();

        nodes.push(
            <ReferenceButton
                key={h.randomString()}
                className={"btn btn-mini btn-warning"}
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
                        className={"btn btn-mini"}
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
            {data} = reference,
            authors =
                reference.data.authors || reference.data.authors_short || reference.NO_AUTHORS_TEXT,
            year = reference.data.year || "";

        return (
            <div id="reference_detail_div">
                {
                    <div className="ref_small">
                        <span>
                            {authors}&nbsp;{year}
                        </span>
                        {showActions ? (
                            <div className="btn-group pull-right">
                                <a className={actionsBtnClassName} data-toggle="dropdown">
                                    Actions&nbsp;<span className="caret"></span>
                                </a>
                                <ul className="dropdown-menu">
                                    <li>
                                        <a href={data.editTagUrl}>Edit tags</a>
                                    </li>
                                    <li>
                                        <a href={data.editReferenceUrl}>Edit reference</a>
                                    </li>
                                    <li>
                                        <a href={data.deleteReferenceUrl}>Delete reference</a>
                                    </li>
                                </ul>
                            </div>
                        ) : null}
                    </div>
                }
                {data.title ? <p className="ref_title">{data.title}</p> : null}
                {data.journal ? <p className="ref_small">{data.journal}</p> : null}
                {data.abstract ? (
                    <div className="abstracts" dangerouslySetInnerHTML={{__html: data.abstract}} />
                ) : null}
                {showTags && data.tags.length > 0 ? (
                    <p>
                        {data.tags.map((d, i) => [
                            <span key={i} className="label label-info">
                                {d.get_full_name()}
                            </span>,
                            <span key={i + 1000}>&nbsp;</span>,
                        ])}
                    </p>
                ) : null}
                {data.searches.length > 0 ? (
                    <p>
                        <strong>HAWC searches/imports:</strong>
                        {data.searches.map((d, i) => (
                            <span key={i}>
                                &nbsp;<a href={d.url}>{d.title}</a>
                            </span>
                        ))}
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
    actionsBtnClassName: "btn btn-small dropdown-toggle",
    showHr: false,
    showTags: true,
};

export default Reference;
