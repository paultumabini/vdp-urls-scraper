async function fetchApi(url) {
  const res = await fetch(url);
  return await res.json();
}

// list of providers
async function addProviderDataList(func, url1, url2) {
  const providerList = await fetchApi(url1);

  const provArr = [...new Set(providerList.map(p => p.name))].sort((a, b) => (a > b ? 1 : -1));
  const input = document.getElementById('id_web_provider');

  input.insertAdjacentHTML('afterbegin', `<datalist id='providerList'></datalist>`);

  provArr.forEach(data => {
    const options = document.createElement('option');
    options.value = data;
    options.textContent = data;
    input.querySelector('#providerList').appendChild(options);
  });

  func(providerList, url2);
}

// populate other dealer info
async function addAimDealerList(providers, url) {
  const aimDealerList = await fetchApi(url);
  const form = document.querySelector('form');

  form.elements.site_name.addEventListener('change', function (e) {
    aimDealerList.forEach(({ dealer_id, site_url, web_provider_id }) => {
      if (dealer_id.toString() === this.value) {
        const domain = site_url.replace(/.+\/\/|www.|\..+|-/g, '');

        form.elements.site_url.value = site_url;
        form.elements.id_site_id.value = domain;
        providers.forEach(({ id, name }) => {
          if (id === web_provider_id) form.elements.web_provider.value = name;
        });
      }
    });

    if (!form.elements.id_site_name.selectedIndex) {
      form.elements.site_url.value = '';
      form.elements.id_site_id.value = '';
      form.elements.web_provider.value = '';
    }
  });
}
