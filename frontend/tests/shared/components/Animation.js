import {render} from "@testing-library/react";
import React, {act} from "react";
import {describe, expect, it} from "vitest";

import Animation from "../../../shared/components/Animation";

describe("Animation", function () {
    it("applies transition CSS styles and animation", async function () {
        const {container} = render(
                <Animation
                    animation={{opacity: 1, width: "100%"}}
                    duration={10}
                    easing={"ease-out"}>
                    <div data-testid="test-child" style={{opacity: 0.5}}>
                        Test content
                    </div>
                </Animation>
            ),
            child = container.querySelector('[data-testid="test-child"]');

        // Check initial styles are as expected
        expect(child.style.opacity).toBe("0.5");
        expect(child.style.width).toBe("");

        // Check transition property is set with correct values
        expect(child.style.transition).toBe("opacity 10ms ease-out, width 10ms ease-out");

        // Wait for requestAnimationFrame to complete
        await act(async () => await new Promise(resolve => requestAnimationFrame(resolve)));

        // Check styles exist after after animation
        expect(child.style.opacity).toBe("1");
        expect(child.style.width).toBe("100%");
    });
});
