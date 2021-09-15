import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import GenericError from "shared/components/GenericError";
import StudyRow from "./StudyRow";

@inject("store")
@observer
class Root extends Component {
    render() {
        const {studies, error} = this.props.store,
            {number_of_reviewers} = this.props.store.config;
        return (
            <>
                {error ? <GenericError /> : null}
                <p>
                    <b>Individual reviews required:</b>&nbsp;{number_of_reviewers}
                </p>
                <table className="table table-condensed table-striped">
                    <colgroup>
                        <col width="20%" />
                        <col width="40%" />
                        <col width="40%" />
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
                </table>
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
