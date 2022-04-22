import * as d3 from "d3";
import h from "shared/utils/helpers";

const getSvgObject = function(svgElement) {
        // save svg and css styles to this document as a blob.
        // Adapted from SVG-Crowbar: https://nytimes.github.io/svg-crowbar/
        // Removed CSS style-grabbing components as this behavior was unreliable.
        const svg = d3.select(svgElement),
            rect = svg.node().getBoundingClientRect();

        svg.attr("version", "1.1");
        svg.attr("xmlns", d3.namespaces.svg);

        return {
            width: Math.ceil(rect.width),
            height: Math.ceil(rect.height),
            source: btoa(escape(new XMLSerializer().serializeToString(svgElement))),
        };
    },
    downloadBlob = (blob, contentDisposition) => {
        // https://stackoverflow.com/a/42274086/906385
        const url = window.URL.createObjectURL(blob),
            a = document.createElement("a"),
            filename = /filename="(.+?)"/.exec(contentDisposition);
        a.href = url;
        a.download = filename ? filename[1] : "download.txt";
        a.className = "hidden";
        document.body.appendChild(a);
        a.click();
        a.remove();
    },
    pollForResult = url => {
        const fetchResult = () => {
            fetch(url, h.fetchGet).then(response => {
                const contentType = response.headers.get("content-type"),
                    contentDisposition = response.headers.get("content-disposition");
                if (contentType == "application/json") {
                    return setTimeout(fetchResult, 5000);
                }
                response.blob().then(blob => downloadBlob(blob, contentDisposition));
            });
        };
        fetchResult();
    },
    rasterize = (svg, format) => {
        const blob = getSvgObject(svg),
            payload = {
                output: format,
                svg: blob.source,
                width: blob.width,
                height: blob.height,
            },
            url = "/assessment/api/rasterize/";

        h.handleSubmit(
            url,
            "POST",
            null,
            payload,
            d => setTimeout(() => pollForResult(d.url), 5000),
            err => console.error(err),
            err => console.error(err)
        );
    };

export default rasterize;
