<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<script>
  // If you created the map as window.map or L.map('id'), hook popupopen:
  // Replace `map` with your actual Leaflet map variable if different.
  (function attachPopupSwiperInit(){
    if (!window.map || !window.L) return;
    window.map.on('popupopen', function(e){
      const root = e.popup.getElement(); // popup container
      if (!root) return;
      root.querySelectorAll('.swiper').forEach(function(container){
        // Avoid double-init
        if (container.__swiper_inited) return;
        container.__swiper_inited = true;

        new Swiper(container, {
          slidesPerView: 1,
          spaceBetween: 10,
          pagination: {
            el: container.querySelector('.swiper-pagination'),
            clickable: true
          }
        });
      });
    });
  })();
</script>
