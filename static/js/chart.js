'use strict';

//datasets
const renderDatasets = (scrapes, barThickness, radius) => {
  return [
    {
      label: `# of Scrapes (Total:${scrapes.reduce((acc, val) => acc + val.totalScrapes, 0).toLocaleString()})`,
      data: [...scrapes.map(s => s.totalScrapes)],
      type: 'bar',
      backgroundColor: ['rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)', 'rgba(255, 206, 86, 0.5)', 'rgba(75, 192, 192, 0.5)', 'rgba(153, 102, 255, 0.5)', 'rgba(255, 159, 64, 0.5)', 'rgba(136, 131, 150, 0.5)', 'rgba(74, 217, 83, 0.5)', 'rgba(247, 0, 243, 0.5)'],
      borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)', 'rgba(136, 131, 150, 1)', 'rgba(74, 217, 83, 1)', 'rgba(247, 0, 243, 1)'],
      borderWidth: 1,
      barThickness: +`${barThickness}`,
      borderRadius: +`${radius}`,
      borderSkipped: false,
      hoverBorderWidth: 2,
    },
  ];
};

//tooltips
const renderTooltips = (label, digit, unit) => {
  const hhmmss = (l, time) => {
    //convert min -> sec -> hh:mm:ss
    const t = time * 60;
    const h = Math.floor(t / 3600)
        .toString()
        .padStart(2, '0'),
      m = Math.floor((t % 3600) / 60)
        .toString()
        .padStart(2, '0'),
      s = Math.floor(t % 60)
        .toString()
        .padStart(2, '0');
    return `${l}: ${h}:${m}:${s}`;
  };

  return {
    callbacks: {
      label: function (context) {
        if (label === 'Elasped') {
          const time = context.raw.toFixed(`${digit}`);
          return hhmmss(label, time);
        }
        return `${label}: ${context.raw.toFixed(`${digit}`)}${unit}`;
      },
      afterBody: function (context) {
        if (label === 'Elasped' || label === 'Scrapes') {
          const data = [];
          const prevIdx = context[0].dataIndex - 1;

          if (prevIdx >= 0) {
            const prevData = context[0].dataset.data[prevIdx];
            const diff = context[0].raw - prevData;
            data.push(`------------------------`);

            data.push(`Diff: ${diff >= 0 ? `+${diff.toFixed(`${digit}`)}` : diff.toFixed(`${digit}`)}${unit}`);

            const percentChange = (diff / prevData) * 100;
            data.push(`% Change: ${percentChange.toFixed(2) + '%'}`);
          } else {
            data.push(`------------------------`);
            data.push(`Diff:  n/a `);
            data.push(`% Change: n/a`);
          }
          return data;
        }
      },
    },
  };
};

// scales
const renderScales = (textX, textY, gridX, gridY) => {
  return {
    yAxes: {
      beginAtZero: true,
      title: {
        display: true,
        text: `${textX}`,
        font: {
          size: 12,
          weight: 'bold',
          lineHeight: 1,
        },
        padding: { top: 0, left: 0, right: 0, bottom: 15 },
      },
      grid: {
        display: `${gridX}` === 'true',
        borderDash: [5, 5],
      },
      ticks: {
        autoSkip: false,
        // stepSize: 0,
        // maxRotation: `${angle}`,
        // minRotation: `${angle}`,
      },
    },
    xAxes: {
      ticks: {
        autoSkip: true,
        // stepSize: 0,
        // maxRotation: `${angle}`,
        // minRotation: `${angle}`,
      },
      grid: {
        display: `${gridY}` === 'true',
        borderDash: [5, 5],
      },
      title: {
        display: true,
        text: `${textY}`,
        font: {
          size: 12,
          weight: 'bold',
          lineHeight: 1,
        },
      },
    },
  };
};

const renderPlugins = (titleText, subText, label, index, unit) => {
  return {
    title: {
      display: true,
      text: titleText,
    },
    legend: {
      labels: {
        usePointStyle: true,
        pointStyle: 'rectRounded',
      },
    },
    subtitle: {
      display: true,
      text: subText,
      color: 'blue',
      font: {
        size: 12,
        family: 'tahoma',
        weight: 'normal',
        style: 'italic',
      },
      padding: {
        bottom: 10,
      },
    },
    tooltip: renderTooltips(label, index, unit),
  };
};

const chartA = scrapeData => {
  const ctx = document.getElementById('chartA__canvas').getContext('2d');
  ctx.setLineDash([5, 15]);
  const myChart = new Chart(ctx, {
    data: {
      labels: [...scrapeData.map(s => `${s.spider_name} (${[...new Set(s.sites)].length})`)],
      datasets: renderDatasets(scrapeData, 8, 20),
    },
    options: {
      indexAxis: 'y', // orientation is vertical
      responsive: true,
      aspectRatio: 1,
      maintainAspectRatio: false,
      scales: renderScales('Templates', 'Items', false, true),
      plugins: renderPlugins(`Scraped Items`, '(Year to date)', 'YTD Scrapes', 0, ''),
    },
  });

  // remove spinner
  document.querySelector('.spinner-pulse').remove();
};

const chartB = scrapeData => {
  const ctx = document.getElementById('chartB__canvas').getContext('2d');
  const gradientBg = ctx.createLinearGradient(0, 0, 100, 0);

  const sortedData = scrapeData.sort((a, b) => (a.dateCreated > b.dateCreated ? 1 : -1));

  const myChart = new Chart(ctx, {
    data: {
      labels: [
        ...sortedData
          .slice(-15) //render the last 30 day scrapeData
          .map(s => `${s.dateCreated} (${s.sites.length})`),
      ],
      datasets: renderDatasets(sortedData.slice(-15), 8, 20),
    },
    options: {
      responsive: true,
      //   aspectRatio: 1,
      //   maintainAspectRatio: false,
      scales: renderScales('Items', '', true, false),
      plugins: renderPlugins('Scraped Items', '(Last 15-day scrapes)', 'Scrapes', 0, ''),
    },
  });

  // remove spinner
  document.querySelector('.spinner-pulse').remove();
};

const chartC = scrapeData => {
  const ctx = document.getElementById('chartC__canvas').getContext('2d');
  const sortedData = scrapeData.sort((a, b) => (a.dateCreated > b.dateCreated ? 1 : -1));

  const gradientBackground = ctx.createLinearGradient(0, 0, 0, 400);
  gradientBackground.addColorStop(0, 'rgba(150, 217, 255,1)');
  gradientBackground.addColorStop(0.6, 'rgba(150, 217, 255,0)');

  const gradientBorder = ctx.createLinearGradient(0, 0, 0, 510);
  gradientBorder.addColorStop(1, 'rgba(45, 174, 247,8)');
  1;

  //   const gradientBackground = ctx.createLinearGradient(500, 0, 100, 0);
  //   const gradientBorder = ctx.createLinearGradient(500, 0, 100, 0);

  //   gradientBackground.addColorStop(1, 'rgba(247, 0, 243, .15)');
  //   gradientBackground.addColorStop(0.5, 'rgba(244, 67, 54, .15)');
  //   gradientBackground.addColorStop(0, 'rgba(71, 57, 250,.15)');

  //   gradientBorder.addColorStop(0, 'rgba(71, 57, 250,.8)');
  //   gradientBorder.addColorStop(0.5, 'rgba(244, 67, 54, .8)');
  //   gradientBorder.addColorStop(1, 'rgba(247, 0, 243, .8)');

  const myChart = new Chart(ctx, {
    data: {
      labels: [...sortedData.slice(-15).map(s => s.dateCreated)], //render the last 30 day scrapeData
      datasets: [
        {
          label: 'Scrape/ Elapsed Time',
          data: [...sortedData.slice(-15).map(s => s.totalElapsed)],
          type: 'line',

          backgroundColor: gradientBackground,
          borderColor: gradientBorder,
          pointBorderColor: gradientBorder,
          pointBackgroundColor: gradientBorder,
          pointHoverBackgroundColor: gradientBorder,
          pointHoverBorderColor: gradientBorder,
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      //   aspectRatio: 1,
      //   maintainAspectRatio: false,
      scales: renderScales('Minutes', 'Days', true, false),
      plugins: {
        legend: {
          labels: {
            usePointStyle: true,
            pointStyle: 'rectRounded',
          },
        },
        tooltip: renderTooltips('Elasped', 2, 'min'),
      },
    },
  });
};

const renderCharting = logs => {
  const output = Object.values(
    logs.reduce(
      (acc, { spider_name, items_scraped, elapsed_time_seconds, allowed_domain }) => (
        (acc[spider_name] ??= {
          spider_name,
          count: 0,
          totalScrapes: 0,
          totalElapsed: 0,
          sites: [],
        }),
        acc[spider_name].count++,
        (acc[spider_name].totalScrapes += +items_scraped),
        (acc[spider_name].totalElapsed += +elapsed_time_seconds),
        acc[spider_name].sites.push(allowed_domain),
        acc
      ),
      {}
    )
  );

  chartA(output);
  filterScrapeDays(logs);
};

//Get Date

const filterScrapeDays = data => {
  const calcDaysPassed = (prevDates, lastDate) => Math.round(Math.abs(lastDate - prevDates) / (1000 * 60 * 60 * 24));
  const daysCreated = data
    .sort((a, b) => (a.date_created > b.date_created ? 1 : -1))
    // .filter(
    //   d =>
    //     calcDaysPassed(
    //       new Date(d.date_created),
    //       new Date(data[data.length - 1].date_created)
    //     ) <= 30
    // )
    .map(obj => {
      const [m, d, y] = new Date(obj.date_created).toLocaleString('en-US' /*{ timeZone: 'US/Pacific' }*/).split(',')[0].split('/');
      return {
        dateCreated: `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`,
        provider: obj.spider_name,
        site: obj.target_site_id,
        scrapes: +obj.items_scraped,
        elaspedTimSec1: +obj.elapsed_time_seconds,
        elaspedTimeSec2: obj.elapsed_time,
      };
    });

  const output = Object.values(
    daysCreated.reduce(
      (acc, { dateCreated, provider, site, scrapes, elaspedTimSec1, elaspedTimeSec2 }) => (
        (acc[dateCreated] ??= {
          dateCreated,
          providers: [],
          sites: [],
          elaspedTimeSec2,
          count: 0,
          totalScrapes: 0,
          totalElapsed: 0,
        }),
        acc[dateCreated].count++,
        (acc[dateCreated].totalScrapes += +scrapes),
        (acc[dateCreated].totalElapsed += +elaspedTimSec1 / 60),
        acc[dateCreated].providers.push(provider),
        acc[dateCreated].sites.push(site),
        acc
      ),
      {}
    )
  );

  chartB(output);
  chartC(output);
};

const getSpiderLogs = () => {
  const spinners = {
    'chart-A': 'chart-A',
    chartBC: 'chart-B-C',
  };

  Object.entries(spinners).forEach(([key, value]) => {
    document.querySelector(`.${value}`).insertAdjacentHTML(
      'beforeend',
      `<div class="spinner-pulse ${key} text-success"> 
         <i class="fa fa-spinner fa-pulse fa-2x fa-fw mt-1"></i> 
       </div>
            `
    );
  });

  $.ajax({
    type: 'GET',
    url: '/spider-log-json/',
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success: function (data) {
      renderCharting(data);
    },
    error: function (error) {
      console.log(error);
    },
  });
};
