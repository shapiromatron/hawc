import { loadConfig } from 'textCleanup/actions/Config';
import * as types from 'textCleanup/constants/ActionTypes';


describe('textCleanup Config action', () => {
    it('should return a config action object', () => {
        let action = loadConfig();

        expect(action).to.deep.equal({
            type: types.CF_LOAD,
        });
    });
});
