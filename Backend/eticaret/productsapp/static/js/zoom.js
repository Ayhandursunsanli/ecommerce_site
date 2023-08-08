const zoomContainers = document.querySelectorAll('.sproduct-imgbox');

    zoomContainers.forEach(container => {
    container.addEventListener('mousemove', e => {
        const boundingRect = container.getBoundingClientRect();
        const x = e.clientX - boundingRect.left;
        const y = e.clientY - boundingRect.top;

        const centerX = boundingRect.width / 2;
        const centerY = boundingRect.height / 2;

        const offsetX = (centerX - x) / 2; // Zoom faktörünü ayarlayabilirsiniz
        const offsetY = (centerY - y) / 2;

        container.querySelector('img').style.transform = `scale(1.5) translate(${offsetX}px, ${offsetY}px)`;
    });

    container.addEventListener('mouseleave', () => {
        container.querySelector('img').style.transform = 'scale(1)';
        });
    });