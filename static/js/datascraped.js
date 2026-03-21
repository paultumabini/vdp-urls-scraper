// load scraped data
'use strict';
const renderTableContent = (fdata, keys) => {
  return fdata
    .reduce((acc, data, i) => {
      keys.map(k => {
        if (!data[k]) data[k] = '';
      });
      acc.push(
        `<tr>
          <td scope="row">${i + 1}</td>
          <td class="scrape">
            <span title="${data.category}">${data.category}</span>
          </td>
          <td class="scrape">
            <span title="${data.year}">${data.year}</span>
          </td>
          <td class="scrape">
            <span title="${data.make}">${data.make}</span>
          </td>
          <td class="scrape">
            <span title="${data.model}">${data.model}</span>
          </td>
          <td class="scrape">
            <span title="${data.trim}">${data.trim}</span>
          </td>
          <td class="scrape">
            <span title="${data.unit}">${data.unit}</span>
          </td>
          <td class="scrape">
            <span class="load__modal darker__primary hover__effect" data-stock-number="${data.stock_number}" data-image-count="${data.images_count}" title="${data.stock_number}" > 
               ${data.stock_number} 
            </span>
          </td>
          <td class="scrape">
            <span title="${data.vin}">${data.vin} </span>
          </td>
          <td class=" scrape td-effect td-overflow">
            <span>
              <a href="${data.vehicle_url ? data.vehicle_url : '#'}"
                target="_blank"
                title="${data.vehicle_url ? data.vehicle_url : '#'}"
                class="lighter__primary hover__effect" >
                ${data.vehicle_url}
              </a>
            </span>
          </td>
          <td class="scrape">
            <span title="${data.msrp}">${data.msrp}</span>
          </td>
          <td class="scrape">
            <span title="${data.price}">${data.price}</span>
          </td>        
          <td class="scrape">
            <span title="${data.rebate}">${data.rebate}</span>
          </td>
          <td class="scrape">
            <span  style="text-align:center" class="load__modal darker__primary hover__effect" title="${data.image_urls}" data-stock-number="${data.stock_number}" data-image-count="${data.images_count}">            
                list           
            </span>
          </td>
          <td class="scrape">
            <span  style="text-align:center" >${data.images_count ? data.images_count : 0}</span>
          </td>
        </tr>`
      );
      return acc;
    }, [])
    .join('');
};

//  if no scrape data
const raiseAlert = (alert, message, reload) => {
  $('.flash-messages-wrapper').empty();
  const alertMessage = `
      <div class="alert alert-${alert}">
      <i class="fas fa-exclamation-circle" ></i> 
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
          <span aria-hidden="true">&times;</span>
      </button>                      
         ${message} 
         ${
           reload
             ? `<button type="button" class="btn btn-info" style="padding:2px 30px; font-size: 12px; font-weight:500; margin-top:5px" onclick="fetchScrapeData()">Yes</button>
             <p style="position:absolute; bottom:-10px; right:10px; color:#bf0f0f">[exit in <span id="countdown">4</span> sec]</p> `
             : ''
         }   
                     
      </div>       
      `;

  let timeleft = 4;
  const timer = setInterval(() => {
    timeleft--;
    document.getElementById('countdown').textContent = timeleft;
    if (timeleft <= 0) clearInterval(timer);
  }, 1000);

  $('.flash-messages-wrapper').append(alertMessage);

  runFuncs();
};

// if scrape data is avaible
const renderTableStructure = fdata => {
  const tableStructure = `        
      <div  class="target-sites scraped__data"> 
          <h3 align="left" class="ml-4 pt-3"> Scraped Data</h3>             
          <table id="scrape-data-table" class="table  table-hover">    
              <thead class="thead-light">
              <tr>
                  <th scope="col" style="width:3%">No</th>
                  <th>Category</th>         
                  <th>Year</th>
                  <th>Make</th>                   
                  <th>Model</th>
                  <th>Trim</th>                    
                  <th>As Unit</th>
                  <th>Stock#</th>                    
                  <th style="width:12%" >VIN</th>                   
                  <th style="width:12%" >Vehicle URL</th>                   
                  <th>MSRP</th>                   
                  <th>Price</th>  
                  <th>Rebate</th>                   
                  <th>Image Urls</th>                   
                  <th class="total-images">Image Count</th>  
              </tr> 
              </thead>
              <tbody id="scrape-data-tbody" > 
              </tbody>
              <tfoot>
                <tr>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th style="text-align: center"></th>
                </tr>
            </tfoot>       
          </table>          
      </div>  
      `;

  const scrapeDetail = document.querySelector('.target-sites-scrape-detail');
  scrapeDetail.insertAdjacentHTML('afterend', tableStructure);

  const tBody = document.getElementById('scrape-data-tbody');
  tBody.insertAdjacentHTML('afterbegin', renderTableContent(fdata, Object.keys(fdata[0])));

  // function with event (e.g.'click', 'mouseover') should be rendered before database
  loadScrapeModal(fdata);

  loadDataTable();

  $('.line__loader').fadeOut(300);
  scrapeDetail.querySelector('.line__loader').remove();

  // scorll down to the botton
  $('.content-container')
    .stop()
    .animate({ scrollTop: $('.content-container')[0].scrollHeight }, 1000);

  //   or usin vanilla js
  //   const elem = document.querySelector('.content-container');
  //   elem.scroll({ top: elem.scrollHeight, behavior: 'smooth' });
};

// fetch scraped data
function fetchScrapeData() {
  // line loader activated and remove existing scraped data table
  $('.target-sites-scrape-detail').nextAll().remove();
  $('.target-sites-scrape-detail').prepend('<div class="line__loader"></div>');

  $.ajax({
    type: 'GET',
    url: '/scrape-data-json/',
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success: function (data) {
      filterResult(data);
      setTimeout(_ => {}, 1000);
    },
    error: function (error) {
      console.log(error);
    },
  });
}

const loadData = _ => {
  if ($('.scraped__data').length) {
    $('.line__loader').remove();
    raiseAlert('warning', 'Scraped data already loaded. Do you want to reload the data?', true);
    return;
  }

  fetchScrapeData();
};

const loadBtn = document.querySelector('#load-scrape-data');
if (loadBtn) loadBtn.addEventListener('click', loadData);

// scrape unit modal
function loadScrapeModal(data) {
  const loadModalBtn = document.querySelectorAll('.load__modal');
  const unitDetailModal = document.querySelector('#unitDetailModal');
  const mBody = unitDetailModal.querySelector('.modal-body');

  function renderData(e) {
    $('#unitDetailModal').modal('show');
    $('.modal-dialog').draggable({ handle: '.modal-header' });

    const { stockNumber, imageCount } = e.target.dataset;
    const labels = {
      'Stock#:': 'stock_number',
      'VIN:': 'vin',
      'Vehicle URL:': 'vehicle_url',
      'Category#:': 'category',
      'Year:': 'year',
      'Model:': 'model',
      'Trim:': 'trim',
      'As a Unit:': 'unit',
      'Msrp:': 'msrp',
      'Price:': 'price',
      'Selling Price:': 'selling_price',
      'Rebate:': 'rebate',
      'Discount:': 'discount',
    };

    //render unit info to modal body
    const markUp = data
      .reduce((acc, val) => {
        if (val.stock_number === stockNumber) {
          acc.push(
            Object.entries(labels).map(([key, value]) => {
              let content = '';
              if (value === 'vehicle_url') {
                content = `
                      <div> 
                          <span style="font-weight:500">${key}</span>
                          <a href="${val[value]}"  target="_blank"  class="lighter__primary hover__effect">
                          ${val[value]}
                          </a> 
                      </div>
                  `;
              } else {
                content = `
                  <div>
                      <span style="font-weight:500">${key}</span>
                      <span>${val[value]}</span>
                  </div>
                  `;
              }
              return content.trim();
            })
          );
        }
        return acc;
      }, [])
      .join('')
      .replace(/,/g, '');

    mBody.innerHTML = '';
    mBody.insertAdjacentHTML('afterbegin', markUp);
    mBody.setAttribute('style', 'text-align:left;font-size: .90rem;');
    mBody.insertAdjacentHTML(
      'beforeend',
      `
        <div class="form-group btn-group__images" >  
             <button type="button" class="btn btn-success btn-sm view-images">View Images</button> 
             <button type="button" class="btn btn-success btn-sm view-list">Images URLs</button>                  
        </div> 
    `
    );
    mBody.insertAdjacentHTML('beforeend', `<div class="images-table"> </div>`);

    //render image urls
    function renderTableData(urlData) {
      return urlData
        .filter(d => d.stock_number === stockNumber)[0]
        .image_urls.split('|')
        .map((url, i) => {
          return `
                <tr>
                  <td>${i + 1}</td>
                  <td>
                      <a href="${url}"  target="_blank"  class="lighter__primary hover__effect">
                      ${url}
                      </a>
                  </td>
                </tr>
           `;
        })
        .join('');
    }

    renderTableStructure();

    function renderTableStructure() {
      const tableStructure = `
          <div class='mt-3'>
              <table id="table_image_urls" class="table  table-hover">    
                  <thead class="thead-light">
                      <tr>  
                          <th>#</th>                   
                          <th>Image URLs (Total: ${imageCount})</th> 
                      </tr> 
                  </thead>
              <tbody id="image-urls-tbody" >                  
              </tbody>
              </table>
          <div>         
          `;

      const imagesTable = document.querySelector('.images-table');

      imagesTable.insertAdjacentHTML('afterbegin', tableStructure);
      const tBody = document.getElementById('image-urls-tbody');
      tBody.insertAdjacentHTML('afterbegin', renderTableData(data));

      $('#table_image_urls').DataTable({
        bDestroy: true,
        sDom: 'ltipr',
        pageLength: 10,
        lengthMenu: [
          [5, 10, 20, 50, 100 - 1],
          [5, 10, 20, 50, 100],
        ],
        language: {
          paginate: {
            previous: '<i class="fas fa-angle-left"></i>',
            next: '<i class="fas fa-angle-right"></i>',
          },
        },
      });
    }

    //view images and list images btns
    const viewImages = document.querySelector('.view-images');
    const viewList = document.querySelector('.view-list');
    const imagesTable = document.querySelector('.images-table');

    viewImages.addEventListener('click', function () {
      imagesTable.innerHTML = '';

      imagesTable.insertAdjacentHTML(
        'afterbegin',
        `<div class="spinner-pulse text-success"> 
             <i class="fa fa-spinner fa-pulse fa-3x fa-fw mt-1"></i> 
        </div>`
      );

      const renderDataCarousel = data
        .filter(d => d.stock_number === stockNumber)[0]
        .image_urls.split('|')
        .map((url, i) => {
          if (i === 0) {
            return `
                    <div class="carousel">
                        <div class="carousel__item carousel__item--visible" data-image-number ="${i + 1}">
                            <a href="${url}"  target="_blank" >
                                <img class="vehicle__images" src="${url}" />
                            </a>  
                        </div>             
                    </div>               
               `;
          } else {
            return `
                    <div class="carousel">
                        <div class="carousel__item" data-image-number ="${i + 1}">
                            <a href="${url}"  target="_blank" >
                                <img class="vehicle__images" src="${url}" />
                            </a>  
                        </div>                    
                    </div>               
               `;
          }
        })
        .join('');

      imagesTable.insertAdjacentHTML('afterbegin', renderDataCarousel);

      // load images
      const images = document.querySelector('.vehicle__images');

      images.addEventListener('load', function () {
        $('.spinner-pulse').remove();
        imagesTable.insertAdjacentHTML(
          'beforeend',
          `
                <div class="carousel__actions">
                    <button id="carousel__button--prev" aria-label="Previous slide">
                        <i class="fa fa-chevron-left" aria-hidden="true"></i>
                    </button>
                    <button id="carousel__button--next" aria-label="Next slide">
                        <i class="fa fa-chevron-right" aria-hidden="true"></i>
                    </button>
                </div>
                <div>
                     <span class="images-total"> <span class="image-number">1</span>/${imageCount} <span>
                </div>
              `
        );

        // carousel
        let slidePosition = 0;
        const slides = document.getElementsByClassName('carousel__item');
        const totalSlides = slides.length;

        function updateSlidePosition() {
          Array.from(slides).forEach(slide => {
            slide.classList.remove('carousel__item--visible');
            slide.classList.add('carousel__item--hidden');
          });

          slides[slidePosition].classList.add('carousel__item--visible');
        }

        function moveToNextSlide() {
          if (slidePosition === totalSlides - 1) slidePosition = 0;
          else slidePosition++;

          updateSlidePosition();
        }

        function moveToPrevSlide() {
          if (slidePosition === 0) slidePosition = totalSlides - 1;
          else slidePosition--;

          updateSlidePosition();
        }

        document.getElementById('carousel__button--next').addEventListener('click', function () {
          moveToNextSlide();
          const { imageNumber } = document.querySelector('.carousel__item--visible').dataset;
          document.querySelector('.image-number').textContent = imageNumber;
        });
        document.getElementById('carousel__button--prev').addEventListener('click', function () {
          moveToPrevSlide();
          const { imageNumber } = document.querySelector('.carousel__item--visible').dataset;
          document.querySelector('.image-number').textContent = imageNumber;
        });
      });

      viewList.addEventListener('click', function () {
        imagesTable.innerHTML = '';
        renderTableStructure();
      });
    }); //view images end
  }

  // load vehicles info modal
  loadModalBtn.forEach(el => {
    el.addEventListener('click', renderData);
  });
}
