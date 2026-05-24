(function () {
  var modal;
  var modalImage;
  var modalCaption;
  var closeButton;
  var lastActiveElement;

  function ensureModal() {
    if (modal) {
      return;
    }

    modal = document.createElement("div");
    modal.className = "image-zoom-modal";
    modal.hidden = true;
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-label", "Full-size image");

    closeButton = document.createElement("button");
    closeButton.className = "image-zoom-close";
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "Close full-size image");
    closeButton.textContent = "x";

    var content = document.createElement("div");
    content.className = "image-zoom-modal-content";

    modalImage = document.createElement("img");
    modalCaption = document.createElement("p");
    modalCaption.className = "image-zoom-caption";

    content.appendChild(modalImage);
    content.appendChild(modalCaption);
    modal.appendChild(closeButton);
    modal.appendChild(content);
    document.body.appendChild(modal);

    closeButton.addEventListener("click", closeModal);
    modal.addEventListener("click", function (event) {
      if (event.target === modal) {
        closeModal();
      }
    });
    document.addEventListener("keydown", function (event) {
      if (!modal.hidden && event.key === "Escape") {
        closeModal();
      }
    });
  }

  function openModal(image, fullSource) {
    ensureModal();

    lastActiveElement = document.activeElement;
    modalImage.src = fullSource || image.currentSrc || image.src;
    modalImage.alt = image.alt || "";
    modalCaption.textContent = image.alt || "";
    modalCaption.hidden = !image.alt;
    modal.hidden = false;
    document.body.classList.add("image-zoom-open");
    closeButton.focus();
  }

  function closeModal() {
    if (!modal || modal.hidden) {
      return;
    }

    modal.hidden = true;
    modalImage.removeAttribute("src");
    document.body.classList.remove("image-zoom-open");

    if (lastActiveElement && typeof lastActiveElement.focus === "function") {
      lastActiveElement.focus();
    }
  }

  document.addEventListener("click", function (event) {
    var target = event.target;
    var button = target && target.closest && target.closest(".image-zoom-button");
    if (!button) {
      return;
    }

    var figure = button.closest(".image-zoomable");
    var image = figure && figure.querySelector("img");
    if (!image) {
      return;
    }

    event.preventDefault();
    openModal(image, button.getAttribute("data-full-src"));
  });
})();
