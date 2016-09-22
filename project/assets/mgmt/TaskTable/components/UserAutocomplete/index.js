import React, { Component, PropTypes } from 'react';

import Autocomplete from 'shared/components/Autocomplete';


class UserAutocomplete extends Component {

    constructor(props) {
        super(props);
        this.getSelectedUserID = this.getSelectedUserID.bind(this);
    }

    componentWillMount() {
        this.url = '/selectable/myuser-assessmentteammemberorhigherlookup'; /* TODO get url from django-selectable in template*/
    }

    getSelectedUserID(){
        return this.refs.owner.state.selected;
    }

    render() {
        return (
            <Autocomplete url={this.url} assessment={this.props.task.study.assessment} placeholder={'Owner'} ref='owner'/>
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
