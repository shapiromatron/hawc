import PropTypes from "prop-types";
import React, {Component} from "react";
import Autocomplete from "shared/components/Autocomplete";

class UserAutocomplete extends Component {
    render() {
        const {onChange, task, url} = this.props;
        let idName = `${task.id}-owner`,
            loaded = {
                display: task.owner ? task.owner.full_name : null,
                id: task.owner ? task.owner.id : null,
            },
            submitUrl = `${url}?assessment_id=${task.study.assessment.id}`;

        return (
            <div className="form-group">
                <label htmlFor={idName}>Owner</label>
                <Autocomplete onChange={onChange} id={idName} url={submitUrl} loaded={loaded} />
            </div>
        );
    }
}

UserAutocomplete.propTypes = {
    task: PropTypes.shape({
        study: PropTypes.shape({
            assessment: PropTypes.object.isRequired,
        }).isRequired,
        owner: PropTypes.shape({
            full_name: PropTypes.string,
            id: PropTypes.number,
        }),
        id: PropTypes.number,
    }).isRequired,
    url: PropTypes.string.isRequired,
    onChange: PropTypes.func,
};

export default UserAutocomplete;
