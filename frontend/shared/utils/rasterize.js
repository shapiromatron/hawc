import * as d3 from "d3";

const URL_TEMPLATES = "/rasterize/",
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
    getSvgString = (svgElement, cb) => {
        fetch(URL_TEMPLATES)
            .then(resp => resp.json())
            .then(d => {
                const svg = d3.select(svgElement);
                svg.attr("version", "1.1");
                svg.attr("xmlns", d3.namespaces.svg);
                const svgStr = new XMLSerializer()
                    .serializeToString(svgElement)
                    .replace(/<svg.*?>/, `$&${d.template}`);
                cb(svgStr);
            });
    },
    toSvg = svgElement => {
        getSvgString(svgElement, svgStr => {
            const blob = new Blob([svgStr], {type: "image/svg+xml"});
            downloadBlob(blob, 'attachment; filename="download.svg"');
        });
    },
    toPng = svgElement => {
        getSvgString(svgElement, svgStr => {
            const canvas = document.createElement("canvas"),
                ctx = canvas.getContext("2d"),
                bb = svgElement.getBoundingClientRect(),
                img = document.createElement("img"),
                height = Math.ceil(bb.height * 5),
                width = Math.ceil(bb.width * 5);

            canvas.height = height;
            canvas.width = width;

            img.setAttribute(
                "src",
                "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgStr)))
            );
            img.onload = function() {
                ctx.drawImage(img, 0, 0, width, height);
                canvas.toBlob(
                    blob => downloadBlob(blob, 'attachment; filename="download.png"'),
                    "image/png"
                );
            };
        });
    },
    rasterize = (svgElement, format) => {
        switch (format) {
            case "svg":
                toSvg(svgElement);
                break;
            case "png":
                toPng(svgElement);
                break;
            default:
                throw `Invalid format ${format}`;
        }
    };

export default rasterize;
