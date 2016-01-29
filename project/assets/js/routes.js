import React from 'react';
import { Route, IndexRoute } from 'react-router';
import urls from './constants/urls';
import AssessmentApp from './containers/AssessmentApp';
import Fields from './containers/Fields'

export default (
  <Route path={urls.assessment.url} >
      <IndexRoute component={AssessmentApp} />
      <Route path={urls.fields.url} component={Fields} />
      {/*<Route path={urls.endpoints.url} component={}*/}
  </Route>
);
