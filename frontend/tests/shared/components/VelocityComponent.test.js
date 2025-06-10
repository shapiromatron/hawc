import React from "react";
import {describe, expect, it} from "vitest";

import VelocityComponent from "../../../shared/components/VelocityComponent";

describe("VelocityComponent", function () {
    it("has correct default props", function () {
        expect(VelocityComponent.defaultProps.duration).toBe(1000);
        expect(VelocityComponent.defaultProps.runOnMount).toBe(false);
    });

    it("accepts required animation prop", function () {
        const props = {
            animation: {opacity: 1, width: "100%"},
            children: React.createElement("div", {}, "test"),
        };

        // Check that component can be instantiated with required props
        const component = new VelocityComponent(props);
        expect(component.props.animation).toEqual({opacity: 1, width: "100%"});
        expect(component.props.children).toBeTruthy();
    });

    it("has proper propTypes defined", function () {
        expect(VelocityComponent.propTypes.animation).toBeTruthy();
        expect(VelocityComponent.propTypes.children).toBeTruthy();
        expect(VelocityComponent.propTypes.duration).toBeTruthy();
        expect(VelocityComponent.propTypes.runOnMount).toBeTruthy();
    });
});
