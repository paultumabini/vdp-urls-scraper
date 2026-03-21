// add avatar image
const runAdminScript = imgUrl => {
  //  change avatar image
  const imgProfile = document.querySelector('.image>img');
  console.log('Hello', imgUrl, imgProfile);
  imgProfile.src = imgUrl;
  // remove jazzmin version
  document.querySelector('.main-footer>div').innerHTML = '';
  document.querySelector('.main-footer>div').innerHTML = '@debian';
};
