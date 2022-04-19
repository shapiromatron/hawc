'use strict';
var page = require('webpage').create(),
    system = require('system'),
    address = system.args[1],
    output = system.args[2],
    renderTimeout = 500,
    pageEvalGetSvgSize = function() {
        var svg = document.querySelector('svg');
        return svg ? svg.getBoundingClientRect() : { top: 0, left: 0, height: 5, width: 5 };
    },
    renderAndExit = function() {
        // Wait for animations, after viewport size change
        window.setTimeout(function() {
            page.render(output);
            phantom.exit();
        }, renderTimeout);
    },
    getPdf = function() {
        var bb = page.evaluate(pageEvalGetSvgSize);

        page.viewportSize = {
            height: 2 * bb.top + bb.height,
            width: 2 * bb.left + bb.width,
        };

        page.paperSize = {
            height: 20 + 2 * bb.top + bb.height + 'px',
            width: 10 + 2 * bb.left + bb.width + 'px',
            margin: '5px',
        };

        renderAndExit();
    },
    getRasterization = function() {
        var bb = page.evaluate(pageEvalGetSvgSize),
            zoomFactor = 3;

        page.zoomFactor = zoomFactor;

        page.clipRect = {
            top: bb.top,
            height: bb.height * zoomFactor + 15,
            left: bb.left,
            width: bb.width * zoomFactor + 15,
        };

        page.viewportSize = {
            height: 2 * bb.top + bb.height * zoomFactor,
            width: 2 * bb.left + bb.width * zoomFactor,
        };

        renderAndExit();
    };

var func = output.substr(-4) === '.pdf' ? getPdf : getRasterization,
    onPageReady = function() {
        window.setTimeout(func, renderTimeout);
    },
    checkReadyState = function() {
        // continue to check until ready-state is complete
        setTimeout(function() {
            var readyState = page.evaluate(function() {
                return document.readyState;
            });
            if (readyState === 'complete') {
                onPageReady();
            } else {
                checkReadyState();
            }
        });
    },
    onLoadFinished = function(status) {
        // page loaded but other resources may not be complete
        if (status === 'success') {
            checkReadyState();
        } else {
            console.error('Unable to load the address!');
            phantom.exit(1);
        }
    };

// start with a large viewport to render maximum-size
page.viewportSize = {
    height: 1440,
    width: 2560,
};

page.open(address, onLoadFinished);
