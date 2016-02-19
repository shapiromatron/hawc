import React from 'react';
import { Route, IndexRoute } from 'react-router';

import urls from 'constants/urls';
import AssessmentApp from 'containers/AssessmentApp';
import FieldSelection from 'containers/FieldSelection';
import Endpoint from 'containers/Endpoint/App';


export default (
  <Route path={urls.assessment.url} >
      <IndexRoute component={AssessmentApp} />
      <Route path={urls.fields.url} component={FieldSelection} />
        <Route path={urls.endpoints.url} component={Endpoint} />
  </Route>
);
