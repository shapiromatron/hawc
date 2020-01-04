import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Provider } from 'react-redux';
import { Switch, Route, BrowserRouter } from 'react-router-dom';

import { loadConfig } from 'shared/actions/Config';

import urls from 'textCleanup/constants/urls';
import AssessmentApp from 'textCleanup/containers/AssessmentApp';
import FieldSelection from 'textCleanup/containers/FieldSelection';
import Items from 'textCleanup/containers/Items/App';

class Root extends Component {
    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        const { store } = this.props;
        return (
            <Provider store={store}>
                <BrowserRouter>
                    <Switch>
                        <Route
                            exact
                            path={urls.assessment.url}
                            render={(routerProps) => <AssessmentApp {...routerProps} />}
                        />
                        <Route
                            exact
                            path={urls.fields.url}
                            render={(routerProps) => <FieldSelection {...routerProps} />}
                        />
                        <Route
                            path={urls.endpoints.url}
                            render={(routerProps) => <Items {...routerProps} />}
                        />
                    </Switch>
                </BrowserRouter>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
