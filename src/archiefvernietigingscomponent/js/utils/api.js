const fetchDefaults = {
    credentials: 'same-origin',  // required for Firefox 60, which is used in werkplekken
};


const fetch = (url, opts) => {
    const options = Object.assign({}, fetchDefaults, opts);
    return window.fetch(url, options);
};

const apiCall = fetch;

const get = async (url, params={}) => {
    if (Object.keys(params).length) {
        const searchparams = new URLSearchParams(params);
        url += `?${searchparams}`;
    }
    const response = await fetch(url);
    if (!response.ok) {
        return {
            ok: response.ok,
            status: response.status
        };
    } else {
        const data = await response.json();
        return {
            ok: response.ok,
            status: response.status,
            data: data
        };
    }
};

export {get, apiCall};
