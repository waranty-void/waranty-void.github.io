const button = document.querySelector('[data-launch]');
if (button) {
  button.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.title = 'Count23 interactive countdown';
    frame.src = 'https://perlytiara.github.io/Count23/';
    frame.allow = 'fullscreen; picture-in-picture';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.setAttribute('allowfullscreen', '');
    button.closest('.viewer').replaceChildren(frame);
    frame.focus();
  });
}
