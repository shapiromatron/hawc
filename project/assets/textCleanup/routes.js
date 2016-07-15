import React from 'react';
import { Route, IndexRoute } from 'react-router';

import urls from 'textCleanup/constants/urls';
import AssessmentApp from 'textCleanup/containers/AssessmentApp';
import FieldSelection from 'textCleanup/containers/FieldSelection';
import Items from 'textCleanup/containers/Items/App';


export default (
	<Route path={urls.assessment.url} >
		<IndexRoute component={AssessmentApp} />
			<Route path={urls.fields.url} component={FieldSelection} />
				<Route path={urls.endpoints.url} component={Items} />
	</Route>
);
