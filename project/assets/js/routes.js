import React from 'react';
import { Route, IndexRoute } from 'react-router';
import AssessmentApp from './containers/AssessmentApp';
import Assessment from './components/Assessment';
// import ModelPage from './containers/ModelPage'
// import SystemPage from './containers/FieldPage'

export default (
  <Route path="/assessment/:id/endpoint_cleanup/" >
      <IndexRoute component={AssessmentApp} />

      {/*<Route path="/assessment/:id/endpoint_cleanup/:type/" component={ModelPage} />*/}
  </Route>
);
