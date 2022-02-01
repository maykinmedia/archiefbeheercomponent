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

export {fetchZaken};
