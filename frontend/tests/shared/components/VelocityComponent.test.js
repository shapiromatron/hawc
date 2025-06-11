import {render} from "@testing-library/react";
import React from "react";
import {describe, expect, it} from "vitest";

import VelocityComponent from "../../../shared/components/VelocityComponent";

describe("VelocityComponent", function () {
    it("has correct default props", function () {
        expect(VelocityComponent.defaultProps.duration).toBe(1000);
        expect(VelocityComponent.defaultProps.easing).toBe("ease-out");
        expect(VelocityComponent.defaultProps.runOnMount).toBe(false);
    });

    it("applies transition CSS styles when runOnMount is false", function () {
        const animation = {opacity: 1, width: "100%"};
        const duration = 10;
        const easing = "ease-in-out";

        const {container} = render(
            <VelocityComponent
                animation={animation}
                duration={duration}
                easing={easing}
                runOnMount={false}>
                <div data-testid="test-child">Test content</div>
            </VelocityComponent>
        );

        const child = container.querySelector('[data-testid="test-child"]');

        // Check that transition property is set with correct values
        expect(child.style.transition).toBe("opacity 10ms ease-in-out, width 10ms ease-in-out");

        // When runOnMount is false, animation styles should not be applied initially
        expect(child.style.opacity).toBe("");
        expect(child.style.width).toBe("");
    });

    it("applies transition CSS styles and animation when runOnMount is true", async function () {
        const animation = {opacity: 1, width: "100%"};
        const duration = 10;
        const easing = "ease-out";

        const {container} = render(
            <VelocityComponent
                animation={animation}
                duration={duration}
                easing={easing}
                runOnMount={true}>
                <div data-testid="test-child">Test content</div>
            </VelocityComponent>
        );

        const child = container.querySelector('[data-testid="test-child"]');

        // Check that transition property is set with correct values
        expect(child.style.transition).toBe("opacity 10ms ease-out, width 10ms ease-out");

        // Wait for requestAnimationFrame to complete
        await new Promise(resolve => requestAnimationFrame(resolve));

        // When runOnMount is true, animation styles should be applied after requestAnimationFrame
        expect(child.style.opacity).toBe("1");
        expect(child.style.width).toBe("100%");
    });

    it("has proper propTypes defined", function () {
        expect(VelocityComponent.propTypes.animation).toBeTruthy();
        expect(VelocityComponent.propTypes.children).toBeTruthy();
        expect(VelocityComponent.propTypes.duration).toBeTruthy();
        expect(VelocityComponent.propTypes.easing).toBeTruthy();
        expect(VelocityComponent.propTypes.runOnMount).toBeTruthy();
    });
});
