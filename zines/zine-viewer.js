function initZineViewer(config) {
    const pdfPages = config.pdfPages;
    const folder = config.folder;
    const soloLastPage = config.soloLastPage;
    const zineTitle = config.zineTitle;

    const lastSpreadPdf = soloLastPage ? pdfPages - 1 : pdfPages;
    const totalTurnPages = 1 + (lastSpreadPdf - 1) * 2 + (soloLastPage ? 1 : 0);
    let currentPdfPage = 1;
    let presentationMode = false;
    let resizeTimer;

    function getPageW() {
        return Math.floor(Math.min(window.innerWidth - 40, 1000) / 2);
    }

    function buildBook() {
        const pageW = getPageW();
        const $book = $('#flipbook');
        $book.empty();

        $book.append(`<div class="page"><img src="${folder}/page-01.jpg" loading="lazy"></div>`);

        for (let i = 2; i <= lastSpreadPdf; i++) {
            const num = String(i).padStart(2, '0');
            const src = `${folder}/page-${num}.jpg`;
            $book.append(`<div class="page" style="background:url('${src}') no-repeat 0 0/200% 100%"></div>`);
            $book.append(`<div class="page" style="background:url('${src}') no-repeat 100% 0/200% 100%"></div>`);
        }

        if (soloLastPage) {
            const num = String(pdfPages).padStart(2, '0');
            $book.append(`<div class="page"><img src="${folder}/page-${num}.jpg" loading="lazy"></div>`);
        }

        $book.turn({ width: pageW, height: pageW, display: 'single', autoCenter: true, gradients: true, acceleration: true });
        updateControls();
    }

    function updateControls() {
        const $book = $('#flipbook');
        const page = $book.turn('page');
        const view = $book.turn('view');
        const maxVisible = Math.max(...view.filter(p => p > 0));
        const pdfPage = page === 1 ? 1
            : (soloLastPage && page === totalTurnPages ? pdfPages
            : Math.ceil((page - 1) / 2) + 1);

        $('#page-indicator').text(`${pdfPage} / ${pdfPages}`);
        $('#prev-btn').prop('disabled', page <= 1);
        $('#next-btn').prop('disabled', maxVisible >= totalTurnPages);
        currentPdfPage = pdfPage;
        gtag('event', 'page_turn', {
            zine_title: zineTitle,
            pdf_page: pdfPage,
            total_pages: pdfPages
        });
        if (pdfPage === pdfPages) {
            gtag('event', 'book_completed', { zine_title: zineTitle });
        }
    }

    function goNext() {
        const $book = $('#flipbook');
        const pageW = getPageW();
        if ($book.turn('display') === 'single') {
            if ($book.turn('page') >= totalTurnPages) return;
            $book.turn('display', 'double');
            $book.turn('size', pageW * 2, pageW);
            $book.turn('page', 2);
            return;
        }
        if (soloLastPage) {
            const view = $book.turn('view');
            const maxVisible = Math.max(...view.filter(p => p > 0));
            if (maxVisible + 1 === totalTurnPages) {
                $book.turn('display', 'single');
                $book.turn('size', pageW, pageW);
                $book.turn('page', totalTurnPages);
                return;
            }
        }
        $book.turn('next');
    }

    function goPrev() {
        const $book = $('#flipbook');
        const pageW = getPageW();
        if ($book.turn('display') === 'single') {
            if ($book.turn('page') <= 1) return;
            $book.turn('display', 'double');
            $book.turn('size', pageW * 2, pageW);
            $book.turn('page', totalTurnPages - 1);
            return;
        }
        const view = $book.turn('view');
        const leftPage = view[0] > 0 ? view[0] : view[1];
        if (leftPage <= 2) {
            $book.turn('display', 'single');
            $book.turn('size', pageW, pageW);
            $book.turn('page', 1);
            return;
        }
        $book.turn('previous');
    }

    function enterPresentation() {
        const el = document.documentElement;
        const req = el.requestFullscreen || el.webkitRequestFullscreen;
        if (!req) return;
        req.call(el).then(function () {
            if (screen.orientation && screen.orientation.lock) {
                screen.orientation.lock('landscape').catch(function () {});
            }
            presentationMode = true;
            $('#present-btn').text('Exit');
            const $book = $('#flipbook');
            const h = Math.floor(window.innerHeight * 0.85);
            $book.turn('display', 'double');
            $book.turn('size', h * 2, h);
        }).catch(function () {});
    }

    function exitPresentation() {
        const exit = document.exitFullscreen || document.webkitExitFullscreen;
        if (exit) exit.call(document);
        if (screen.orientation && screen.orientation.unlock) screen.orientation.unlock();
        presentationMode = false;
        $('#present-btn').text('Present');
        const $book = $('#flipbook');
        const pageW = getPageW();
        const isLandscape = window.innerWidth > window.innerHeight;
        if (isLandscape) {
            $book.turn('display', 'double');
            $book.turn('size', pageW * 2, pageW);
        } else {
            $book.turn('display', 'single');
            $book.turn('size', pageW, pageW);
        }
    }

    $(document).ready(function () {
        buildBook();
        $('#next-btn').on('click', goNext);
        $('#prev-btn').on('click', goPrev);
        $('#flipbook').on('turned', updateControls);
        $('#present-btn').on('click', function () {
            if (presentationMode) {
                exitPresentation();
            } else {
                enterPresentation();
            }
        });
        $(document).keydown(function (e) {
            if (e.key === 'ArrowRight') goNext();
            if (e.key === 'ArrowLeft') goPrev();
        });
    });

    ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (evt) {
        document.addEventListener(evt, function () {
            if (!document.fullscreenElement && !document.webkitFullscreenElement) {
                if (presentationMode) exitPresentation();
            }
        });
    });

    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            if (presentationMode) return;
            const $book = $('#flipbook');
            const pageW = getPageW();
            const isLandscape = window.innerWidth > window.innerHeight;
            const page = $book.turn('page');
            const isCover = page === 1;
            const isBack = soloLastPage && page === totalTurnPages;

            if (isLandscape && !isCover && !isBack) {
                $book.turn('display', 'double');
                $book.turn('size', pageW * 2, pageW);
            } else {
                $book.turn('display', 'single');
                $book.turn('size', pageW, pageW);
            }
        }, 200);
    });

    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'hidden') {
            gtag('event', 'book_exit_page', {
                zine_title: zineTitle,
                exit_pdf_page: currentPdfPage,
                total_pages: pdfPages
            });
        }
    });
}
