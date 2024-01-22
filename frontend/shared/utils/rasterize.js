import * as d3 from "d3";

const URL_TEMPLATES = "/rasterize/",
    downloadBlob = (blob, contentDisposition) => {
        // https://stackoverflow.com/a/42274086/906385
        if (!blob) {
            alert("An error occurred; no download available.");
            return;
        }
        const url = window.URL.createObjectURL(blob),
            a = document.createElement("a"),
            filename = /filename="(.+?)"/.exec(contentDisposition);
        a.href = url;
        a.download = filename ? filename[1] : "download.txt";
        a.className = "hidden";
        a.target = "_blank";
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
    drawBorder = (ctx, width, height) => {
        /*
        Draw a black border around the image, if one was present in the top-left pixel.
        For some reason, the default image does include the top and left borders, but not the
        bottom or right borders.
        */
        // get top-left pixel and check if RGB is dark; and if so, redraw the border
        const data = ctx.getImageData(0, 0, 1, 1).data;
        if (data[0] < 50 && data[1] < 50 && data[2] < 50) {
            // if so, draw a rectangle. canvas stroke styles are middle-aligned, so to
            // draw a stroke around the full border, offset by 2.
            ctx.strokeStyle = "black";
            ctx.lineWidth = 4;
            ctx.strokeRect(2, 2, width - 2, height - 2);
        }
    },
    toSvg = svgElement => {
        getSvgString(svgElement, svgStr => {
            const blob = new Blob([svgStr], {type: "image/svg+xml"});
            downloadBlob(blob, 'attachment; filename="download.svg"');
        });
    },
    getScalingFactor = maxDim => {
        // There is a maximum canvas size of 32767; we make sure we don't go beyond this
        // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas#maximum_canvas_size
        return maxDim * 5 > 32000 ? 32000 / maxDim : 5;
    },
    toRaster = (svgElement, mime) => {
        getSvgString(svgElement, svgStr => {
            const canvas = document.createElement("canvas"),
                ctx = canvas.getContext("2d"),
                bb = svgElement.getBoundingClientRect(),
                img = document.createElement("img"),
                scaling = getScalingFactor(Math.max(bb.height, bb.width)),
                height = Math.ceil(bb.height * scaling),
                width = Math.ceil(bb.width * scaling),
                imgData = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgStr))),
                extension = mime.slice(mime.match("/").index + 1);

            // set canvas size equal to the image plus a few extra pixels for border
            canvas.height = height + 3;
            canvas.width = width + 3;

            // (debugging only)
            // $("<div>").attr("class", "p-2 m-2").css("background", "orange").appendTo("#main-content-container").append($(canvas));

            img.setAttribute("src", imgData);
            img.onload = function () {
                ctx.drawImage(img, 0, 0, width, height);
                drawBorder(ctx, width, height);
                canvas.toBlob(
                    blob => downloadBlob(blob, `attachment; filename="download.${extension}"`),
                    mime,
                    0.95
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
                toRaster(svgElement, "image/png");
                break;
            case "jpeg":
                toRaster(svgElement, "image/jpeg");
                break;
            default:
                throw `Invalid format ${format}`;
        }
    };

export default rasterize;
