import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import Terms from "./components/VocabTermFields";
import {ehvFields, toxRefDBFields} from "./constants";

@inject("store")
@observer
class App extends Component {
    render() {
        const vocabFields = {null: ehvFields, 1: ehvFields, 2: toxRefDBFields},
            fields = vocabFields[this.props.store.config.vocabulary];
        return <Terms termFields={fields} />;
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
