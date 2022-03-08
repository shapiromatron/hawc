import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import Alert from "shared/components/Alert";
import StudyRow from "./StudyRow";

@inject("store")
@observer
class Root extends Component {
    render() {
        const {studies, error} = this.props.store,
            {number_of_reviewers, edit} = this.props.store.config;
        return (
            <>
                {error ? <Alert /> : null}
                <p>
                    <b>Individual reviews required:</b>&nbsp;{number_of_reviewers}
                </p>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="25%" />
                        <col width="37%" />
                        <col width="37%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Study</th>
                            <th>Individual reviews</th>
                            <th>Final reviews</th>
                        </tr>
                    </thead>
                    <tbody>
                        {studies.map(study => (
                            <StudyRow key={study.id} study={study} />
                        ))}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="3">
                                <ul className="list-unstyled">
                                    <li>
                                        <i className="fa fa-fw fa-times"></i> incomplete: a judgment
                                        and descriptive text are not completed for all metrics.
                                    </li>
                                    <li>
                                        <i className="fa fa-fw fa-check"></i> complete: a judgment
                                        and descriptive text are filled for all metrics.
                                    </li>
                                    {edit ? (
                                        <>
                                            <li>
                                                <i className="fa fa-fw fa-toggle-on"></i> active:
                                                the assigned user will need to complete the review.
                                                For individual reviews, it must be completed before
                                                a final review can be edited. For a final review, it
                                                will be shown as the overall study review. Only one
                                                final review can be active at at time.
                                            </li>
                                            <li>
                                                <i className="fa fa-fw fa-toggle-off"></i> inactive:
                                                the review is retained, but is not visible to team
                                                members. It does not need to be completed, and is
                                                not shown when conducting a final review.
                                            </li>
                                        </>
                                    ) : null}
                                </ul>
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
