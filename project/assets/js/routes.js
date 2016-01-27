import React from 'react';
import { Route } from 'react-router';
import Assessment from './containers/Assessment';
import ModelPage from './containers/ModelPage'
// import SystemPage from './containers/FieldPage'

export default (
  <Route path="/assessment/:id/endpoint_cleanup/" component={Assessment}>
      <Route path="/assessment/:id/endpoint_cleanup/:type/" component={ModelPage} />
  </Route>
);
