import {get} from '../utils/api';

const fetchZaken = async (path, filters, queryParams) => {
    let searchUrl = new URL(window.location.href);
    searchUrl.pathname = path;

    if (filters.zaaktypen?.length) queryParams['zaaktype__in'] = filters.zaaktypen;
    if (filters.bronorganisaties?.length) queryParams['bronorganisatie__in'] = filters.bronorganisaties;
    if (!!filters.identificatie) queryParams['identificatie'] = filters.identificatie;

    const urlSearchParams = new URLSearchParams(queryParams);

    for (const [paramKey, paramValue] of urlSearchParams.entries()) {
        searchUrl.searchParams.set(paramKey, paramValue);
    }

    return await get(searchUrl);
};

function loadLocaleData(locale) {
  switch (locale) {
    case 'nl':
      return import('../compiled-lang/nl.json');
    default:
      return import('../compiled-lang/en.json');
  }
}

export {fetchZaken, loadLocaleData};
