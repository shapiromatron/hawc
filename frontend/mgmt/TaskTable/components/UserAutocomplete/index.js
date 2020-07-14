import React, {Component} from "react";
import PropTypes from "prop-types";

import Autocomplete from "shared/components/Autocomplete";

class UserAutocomplete extends Component {
    constructor(props) {
        super(props);
        this.getPopulatedOwner = this.getPopulatedOwner.bind(this);
        this.url = `${this.props.url}?related=${props.task.study.assessment.id}`;
    }

    getPopulatedOwner() {
        return {
            display: this.props.task.owner ? this.props.task.owner.full_name : null,
            id: this.props.task.owner ? this.props.task.owner.id : null,
        };
    }

    render() {
        let idName = `${this.props.task.id}-owner`,
            loaded = this.getPopulatedOwner();
        return (
            <div>
                <label className="control-label" htmlFor={idName}>
                    Owner
                </label>
                <Autocomplete
                    onChange={this.props.onChange}
                    id={idName}
                    url={this.url}
                    loaded={loaded}
                />
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
