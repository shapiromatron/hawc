import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import Terms from "./components/VocabTermFields";
import {ehvFields, toxrefFields} from "./constants";

@inject("store")
@observer
class App extends Component {
    render() {
        const vocabFields = {ehv: ehvFields, toxref: toxrefFields},
            fields = vocabFields[this.props.store.config.vocabulary_url];
        return <Terms termFields={_.isUndefined(fields) ? ehvFields : fields} />;
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
