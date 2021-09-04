import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";
import h from "shared/utils/helpers";

const handleClick = (csrf, rob) => {
    const url = `/rob/api/review/${rob.id}/update_v2/`,
        payload = _.clone(rob);

    payload.active = !payload.active;
    h.handleSubmit(
        url,
        "PATCH",
        csrf,
        payload,
        d => console.log("success", d),
        d => console.log("failure", d),
        d => console.log("error", d)
    );
};

@inject("store")
@observer
class RobItem extends Component {
    render() {
        const {rob} = this.props,
            {csrf} = this.props.store.config;

        return (
            <p key={rob.id}>
                {rob.author_name}
                <button onClick={() => handleClick(csrf, rob)} className="btn btn-primary">
                    {rob.active ? "Inactivate" : "Activate"}
                </button>
                <button className="btn btn-primary">Reassign</button>
            </p>
        );
    }
}

const StudyRow = observer(props => {
    const {study} = props;

    const individuals = study.robs.filter(rob => !rob.final),
        finals = study.robs.filter(rob => rob.final);

    return (
        <tr>
            <td>
                <a href={study.url} target="_blank" rel="noreferrer">
                    {study.short_citation}
                </a>
            </td>
            <td>
                {individuals.length > 0 ? (
                    individuals.map(rob => <RobItem key={rob.id} rob={rob} />)
                ) : (
                    <p>No individual reviews created.</p>
                )}
                <p>
                    <button className="btn btn-primary">Create new</button>
                </p>
            </td>
            <td>
                {finals.length > 0 ? (
                    finals.map(rob => <RobItem key={rob.id} rob={rob} />)
                ) : (
                    <p>No final reviews created.</p>
                )}
                <p>
                    <button className="btn btn-primary">Create new</button>
                </p>
            </td>
        </tr>
    );
});

@inject("store")
@observer
class Root extends Component {
    render() {
        const {studies} = this.props.store.config;
        return (
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
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
