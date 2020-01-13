import {loadConfig} from "shared/actions/Config";
import * as sharedTypes from "shared/constants/ActionTypes";

describe("textCleanup Config action", () => {
    it("should return a config action object", () => {
        let action = loadConfig();

        expect(action).to.deep.equal({
            type: sharedTypes.CF_LOAD,
        });
    });
});
