import * as d3 from "d3";
import h from "shared/utils/helpers";
import {saveAs} from "file-saver";

const getSvgObject = function(svgElement) {
        // save svg and css styles to this document as a blob.
        // Adapted from SVG-Crowbar: http://nytimes.github.com/svg-crowbar/
        // Removed CSS style-grabbing components as this behavior was unreliable.
        const get_selected_svg = function(svg) {
                svg.attr("version", "1.1");
                svg.attr("xmlns", d3.namespaces.svg);
                var source = new XMLSerializer().serializeToString(svg.node()),
                    rect = svg.node().getBoundingClientRect();
                return {
                    width: Math.ceil(rect.width),
                    height: Math.ceil(rect.height),
                    classes: svg.attr("class"),
                    id: svg.attr("id"),
                    childElementCount: svg.node().childElementCount,
                    source: [source],
                };
            },
            svg = d3.select(svgElement),
            svg_object = get_selected_svg(svg);

        svg_object.blob = new Blob(svg_object.source, {type: "text/xml"});
        return svg_object;
    },
    pollForResult = url => {
        console.log(url);

        // if it's json; set timeout, if its something else, download

        // const fetchResult = () => {
        //     fetch(url, h.fetchGet)
        //         .then(response => response.json())
        //         .then(d => {
        //             if (d.status === "ok") {
        //                 const blob = new Blob([d.data.data], {type: d.data.mime});
        //                 return saveAs(blob);
        //             }
        //             setTimeout(fetchResult, 5000);
        //         });
        // };
        // fetchResult();
    },
    rasterize = (svg, format) => {
        const blob = getSvgObject(svg),
            payload = {
                output: format,
                svg: btoa(escape(blob.source[0])),
                width: blob.width,
                height: blob.height,
            },
            url = "/assessment/api/rasterize/";

        h.handleSubmit(
            url,
            "POST",
            null,
            payload,
            d => pollForResult(d.url),
            err => console.error(err),
            err => console.error(err)
        );
    };

export default rasterize;
