const renderPdf = function (url) {
    var pdfDoc = null,
        pageNum = 1,
        pageRendering = false,
        pageNumPending = null,
        scale = 1,
        canvas = document.getElementById('pdf-canvas'),
        ctx = canvas.getContext('2d'),
        renderPage = function (num) {
            pageRendering = true;
            // Using promise to fetch the page
            pdfDoc.getPage(num).then(function (page) {
                var viewport = page.getViewport({ scale: scale });
                canvas.height = viewport.height;
                canvas.width = viewport.width;

                // Render PDF page into canvas context
                var renderContext = {
                    canvasContext: ctx,
                    viewport: viewport
                };
                var renderTask = page.render(renderContext);

                // Wait for rendering to finish
                renderTask.promise.then(function () {
                    pageRendering = false;
                    if (pageNumPending !== null) {
                        // New page rendering is pending
                        renderPage(pageNumPending);
                        pageNumPending = null;
                    }
                });

                document.getElementById('page_num').textContent = num;
            });
        }, queueRenderPage = function (num) {
            if (pageRendering) {
                pageNumPending = num;
            } else {
                renderPage(num);
            }
        },
        onPrevPage = function () {
            if (pageNum <= 1) {
                return;
            }
            pageNum--;
            queueRenderPage(pageNum);
        }, onNextPage = function () {
            if (pageNum >= pdfDoc.numPages) {
                return;
            }
            pageNum++;
            queueRenderPage(pageNum);
        }

    document.getElementById('next').addEventListener('click', onNextPage);
    document.getElementById('prev').addEventListener('click', onPrevPage);
    pdfjsLib.getDocument(url).promise.then(function (pdfDoc_) {
        pdfDoc = pdfDoc_;
        document.getElementById('page_count').textContent = pdfDoc.numPages;
        renderPage(pageNum);
    });
}
