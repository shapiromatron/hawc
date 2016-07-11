"use strict";
var page = require('webpage').create(),
    system = require('system'),
    address = system.args[1],
    output = system.args[2],
    pageEvalGetSvgSize = function(){
        var d = document.querySelector('svg').getBoundingClientRect();
        return {
            top: d.top,
            height: d.height,
            left: d.left,
            width: d.width,
        };
    },
    getPdf = function(){
        var svg = page.evaluate(pageEvalGetSvgSize);

        page.viewportSize = {
            height: (2 * svg.top + svg.height),
            width: (2 * svg.left + svg.width),
        };

        page.paperSize = {
            height: (20 + 2 * svg.top + svg.height) + 'px',
            width: (10 + 2 * svg.left + svg.width) + 'px',
            margin: '5px',
        };

        page.render(output);
        phantom.exit();
    }, getRasterization = function(){
        var svg = page.evaluate(pageEvalGetSvgSize);
        var zoomFactor = 3;

        page.zoomFactor = zoomFactor;

        page.clipRect = {
            top: svg.top,
            height: svg.height * zoomFactor + 15,
            left: svg.left,
            width: svg.width * zoomFactor + 15,
        };

        page.viewportSize = {
            height: 20 + svg.top + svg.height * zoomFactor,
            width: 20 + svg.left + svg.width * zoomFactor,
        };

        page.render(output);
        phantom.exit();
    };

var func = (output.substr(-4) === '.pdf') ? getPdf : getRasterization,
    onPageReady = function(){
        window.setTimeout(func, 500);
    },
    checkReadyState = function() {
        // continue to check until ready-state is complete
        setTimeout(function () {
            var readyState = page.evaluate(function () {
                return document.readyState;
            });
            if (readyState === 'complete') {
                onPageReady();
            } else {
                checkReadyState();
            }
        });
    },
    onLoadFinished = function (status) {
        // page loaded but other resources may not be complete
        if (status === 'success') {
            checkReadyState();
        } else {
            console.log('Unable to load the address!');
            phantom.exit(1);
        }
    };

// start with a large viewport to render maximum-size
page.viewportSize = {
    height: 1440,
    width: 2560,
};


page.open(address, onLoadFinished);
