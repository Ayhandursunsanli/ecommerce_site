$('.owl-carouselone').owlCarousel({
    loop: true,
    margin: 10,
    nav: false,
    dots: false,
    responsive: {
        0: {
            items: 1
        },
        600: {
            items: 2
        },
        992: {
            items: 3
        },
        1000: {
            items: 4
        },
        1100: {
            items: 5
        }
    }
});

$('.owl-carouseltwo').owlCarousel({
    loop: true,
    margin: 10,
    nav: false,
    dots: false,
    autoplay: true,
    autoplayTimeout: 5000,
    responsive: {
        0: {
            items: 1
        },
        600: {
            items: 1
        },
        1000: {
            items: 1
        }
    }
});
