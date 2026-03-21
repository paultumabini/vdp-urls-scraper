// register
const inputs = document.querySelectorAll('.input');
const checkBox = document.querySelector('#show-pass');
const inputPassword = document.querySelectorAll('.input-password');
const eyes = document.querySelector('span.eyes');
const openEye = document.querySelector('.fa-eye');
const slashEye = document.querySelector('.fa-eye-slash');

function action(e) {
  const parent = e.target.parentNode.parentNode;
  if (e.type === 'focus') parent.classList.add(this);
  if (e.type === 'blur' && e.target.value == '') parent.classList.remove(this);
}

inputs.forEach((input) => (input.addEventListener('focus', action.bind('focus')), input.addEventListener('blur', action.bind('focus'))));

// password viewer

if (checkBox) {
  checkBox.addEventListener('click', function (e) {
    inputPassword.forEach((el) => {
      if (this.checked) el.type = 'text';
      else el.type = 'password';
    });
  });
}

//login
if (eyes) {
  eyes.addEventListener('click', function (e) {
    console.log('hello');
    const input = this.previousSibling.previousSibling;
    if (input.type === 'password') {
      openEye.style.visibility = 'hidden';
      slashEye.style.visibility = 'visible';
      input.type = 'text';
    } else {
      slashEye.style.visibility = 'hidden';
      openEye.style.visibility = 'visible';
      input.type = 'password';
    }
  });
}

$(document).ready(function () {
  // flash message
  $('.alert-success, .alert-danger').each(function () {
    $(this)
      .fadeTo(5000, 1)
      .slideUp(100, function () {
        $(this).remove();
      });
  });
});
