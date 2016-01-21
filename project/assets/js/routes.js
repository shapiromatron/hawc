import React from 'react';
import { Route } from 'react-router';
import EndpointType from './containers/EndpointType';
import ModelPage from './containers/ModelPage'
// import SystemPage from './containers/FieldPage'

export default (
  <Route path="/assessment/:id/endpoint_cleanup/" component={EndpointType}>
      <Route path="/assessment/:id/endpoint_cleanup/:type/" component={ModelPage} />
  </Route>
);
