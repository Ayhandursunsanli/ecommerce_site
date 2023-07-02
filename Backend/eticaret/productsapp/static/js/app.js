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


document.addEventListener("DOMContentLoaded", function () {
    var defaultRenk = "black";
    renkDegistir(defaultRenk);
});

function renkDegistir(renk) {
    var urunGorsel = document.getElementById("product-image").querySelector("img");
    var renkButonlari = document.getElementsByClassName("color-button");
    var price = document.querySelector(".price");

    for (var i = 0; i < renkButonlari.length; i++) {
        renkButonlari[i].classList.remove("activebutton");
    }

    if (renk === "black") {
        urunGorsel.src = "https://st3.myideasoft.com/idea/ha/74/myassets/products/920/vinner-oslo-siyah-kaplama-tek-ayakli-metal-lambader-siyah-25869.jpeg?revision=1683469743";
        price.innerHTML = "1.500 TL";
    } else if (renk === "white") {
        urunGorsel.src = "https://st.myideasoft.com/idea/ha/74/myassets/products/919/vinner-oslo-siyah-kaplama-tek-ayakli-metal-lambader-krom-seritli-hasir-beyaz-25840.jpeg?revision=1683469591";
        price.innerHTML = "1.750 TL";
    } else if (renk === "orange") {
        urunGorsel.src = "https://st1.myideasoft.com/idea/ha/74/myassets/products/045/vinner-ottowa-eskitme-tekli-kure-burgulu-metal-lambader-gold-seritli-mataro-vizon-7454.jpeg?revision=1685720664";
        price.innerHTML = "2.000 TL";
    }
}


// product details

var MainImg = document.getElementById('MainImg');
var smallimg = document.getElementsByClassName('small-img');

smallimg[0].onclick = function () {
    MainImg.src = smallimg[0].src;
}
smallimg[1].onclick = function () {
    MainImg.src = smallimg[1].src;
}
smallimg[2].onclick = function () {
    MainImg.src = smallimg[2].src;
}




