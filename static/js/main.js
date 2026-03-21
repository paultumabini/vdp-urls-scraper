'use strict';

function runFuncs() {
  $(document).ready(function () {
    // sidebar
    $('#sidebarCollapse').on('click', function () {
      $(this).toggleClass('open');
      $('#sidebar').toggleClass('active');
    });
    // dropdown
    $('.dropdown-toggle-main').click(function () {
      $(this).toggleClass('active-highlight');
      $(this).find('.fa-angle-down,.fa-angle-up').toggleClass('fa-angle-down').toggleClass('fa-angle-up');
      $('.dashboard, .help').removeClass('active-highlight');
    });
    //help
    $('.toggle-icon-control').click(function () {
      $(this).find('.fa-plus-square-o, .toggle-icon').toggleClass('fa-plus-square-o').toggleClass('fa-minus-square-o');
      $(this).toggleClass('question-style ');
    });
    //  tooltip
    $('[data-toggle="tooltip"]').tooltip();
    //checkboxes:click event
    $('.check__all').on('click', function () {
      $(':checkbox').prop('checked', true);
    });
    $('.uncheck__all').on('click', function () {
      $(':checkbox').prop('checked', false);
    });
    // flash message
    $('.alert-success, .alert-warning').each(function () {
      $(this)
        .fadeTo(4000, 1)
        .slideUp(100, function () {
          $(this).remove();
        });
    });
  });
}

runFuncs();

// Data Tables
function loadDataTable() {
  var table = $('#dealers-list-table').DataTable({
    stateSave: true,
    bDestroy: true,
    pageLength: 10,
    lengthMenu: [
      [5, 10, 20, 50, 100 - 1],
      [5, 10, 20, 50, 100],
    ],
    //scrollY: 500,
    scrollX: false,
    scroller: true,
    dom: 'lCfrtip',
    order: [],
    colVis: {
      buttonText: '',
      overlayFade: 0,
      align: 'right',
    },
    language: {
      lengthMenu: '_MENU_ entries per page',
      search: '<i class="fa fa-search"></i>',
      searchPlaceholder: 'Search here',
      paginate: {
        previous: '<i class="fas fa-angle-left"></i>',
        next: '<i class="fas fa-angle-right"></i>',
      },
    },
  });
  table
    .columns(4)
    .search('\\b' + '' + '\\b', true, false, true)
    .draw(4);
  $('#scrape-status').on('change', function () {
    table
      .columns(4)
      .search('\\b' + $(this).val() + '\\b', true, false, true)
      .draw();
  });
  $('#site-provider').on('change', function () {
    table.columns(3).search(this.value).draw();
  });

  $('#scrape-data-table').DataTable({
    stateSave: true,
    bDestroy: true,
    language: {
      lengthMenu: '_MENU_ entries per page',
      search: '<i class="fa fa-search"></i>',
      searchPlaceholder: 'Search here',
      paginate: {
        previous: '<i class="fas fa-angle-left"></i>',
        next: '<i class="fas fa-angle-right"></i>',
      },
    },
    footerCallback: function (tfoot, data, start, end, display) {
      var api = this.api();
      $(api.columns('.total-images').footer()).html(
        'Total: ' +
          api
            .columns('.total-images')
            .data()[0]
            .reduce(function (a, b) {
              return a + parseInt(b.replace(/([^0-9\\.])/g, ''));
            }, 0)
      );
    },
  });
}

loadDataTable();

// Nav Profile Image
const profile = document.querySelector('.profile');
const profileMenu = document.querySelector('.menu');
const focusExtend = document.querySelector('.extend-focus');
const togglerBtn = document.querySelector('.navbar-toggler');
const targetElements = [profile, profileMenu, focusExtend];

const mouseEvents = {
  mouseover: 'add',
  mouseout: 'remove',
  click: 'add',
};

togglerBtn.addEventListener('mouseover', () => (profileMenu.style.display = 'none'));

targetElements.forEach(el => {
  Object.entries(mouseEvents).forEach(([event, action]) => {
    el.addEventListener(`${event}`, function (e) {
      profileMenu.style.display = 'block';
      profileMenu.classList[action]('active');
      if (e.type === 'mouseover') {
        focusExtend.classList.add('active');
        profileMenu.classList.add('active');
      }
      if (e.type === 'mouseout' && focusExtend.classList.contains('active')) {
        focusExtend.classList.remove('active');
      }
    });
  });
});

// counter
$('.value').each(function () {
  $(this)
    .prop('Counter', 0)
    .animate(
      {
        Counter: $(this).attr('data-target').replace(/\D/g, ''),
      },
      {
        duration: 3000,
        easing: 'swing',
        step: function (num) {
          $(this).text(`${Math.ceil(num).toLocaleString()}`);
        },
      }
    );
});

// delete message modal
function confirmDeleteMessage(project, site) {
  $('.openDeleteModal').on('click', function () {
    $('#siteDeleteModal').modal('show');
    $('.modal-dialog').draggable({ handle: '.modal-header' });

    const { entryCode, siteName, siteId } = $(this).data();

    console.log('TAI', $(this).data());

    $('#site-to-delete').text(siteName);
    $('#delete-form').attr('action', `/project/${project}/${site}/${siteId}/delete`);
  });
}

// avoid uncaught RefErr: deleteItemModas is not defined or use `if statement`
typeof deleteItemModal === 'function' && deleteItemModal(confirmDeleteMessage);
