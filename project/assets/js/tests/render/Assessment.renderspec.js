import React from 'react';
import TestUtils from 'react-addons-test-utils';
import unexpected from 'unexpected';
import unexpectedReact from 'unexpected-react';

import Assessment from 'components/Assessment';
import { HOST } from 'tests/constants';


const expect = unexpected.clone().use(unexpectedReact);

describe('Assessment component', () => {
    let object, renderer, output;

    beforeEach(() => {
        object = {
            items: [
                {
                    'count': 334,
                    'type': 'epi',
                    'title': 'epidemiological outcomes assessed',
                    'url': `${HOST}/epi/api/cleanup/?assessment_id=57`,
                },
                {
                    'count': 1,
                    'title': 'in vitro endpoints',
                    'type': 'iv',
                    'url': `${HOST}/in-vitro/api/cleanup/?assessment_id=57`,
                },
            ],
            name: 'test assessment',
        };

        renderer = TestUtils.createRenderer();
        renderer.render(<Assessment object={object} />);
        output = renderer.getRenderOutput();
    });

    it('should render with a correct class name', () => {
        expect(output.props.className, 'to equal', 'assessment');
    });

    it('should have a list title', () => {
        expect(output.props.children[0].props.children.join(''), 'to equal', 'Cleanup test assessment');
    });

    it('should render two endpoint types', () => {
        expect(output.props.children[0].props.children.length, 'to equal', 2);
    });

});
