import React, { Component, PropTypes } from 'react';

import Autocomplete from 'shared/components/Autocomplete';


class UserAutocomplete extends Component {

    constructor(props) {
        super(props);
        this.getSelectedUserID = this.getSelectedUserID.bind(this);
        this.getPopulatedOwner = this.getPopulatedOwner.bind(this);
    }

    componentWillMount() {
        this.url = '/selectable/myuser-assessmentteammemberorhigherlookup'; /* TODO get url from django-selectable in template*/
    }

    getPopulatedOwner() {
        return {
            display: this.props.task.owner ? this.props.task.owner.full_name : null,
            id: this.props.task.owner ? this.props.task.owner.id : null,
        };
    }

    getSelectedUserID() {
        return this.refs.owner.state.selected;
    }

    render() {
        let idName = `${this.props.task.id}-owner`,
            loaded = this.getPopulatedOwner();
        return (
            <div>
                <label htmlFor={idName}>Owner</label>
                <Autocomplete
                    id={idName}
                    url={this.url}
                    assessment={this.props.task.study.assessment}
                    loaded={loaded}
                    ref='owner'/>
            </div>
        );
    }
}

UserAutocomplete.propTypes = {
    task: PropTypes.shape({
        study: PropTypes.shape({
            assessment: PropTypes.number.isRequired,
        }).isRequired,
    }).isRequired,
};

export default UserAutocomplete;
