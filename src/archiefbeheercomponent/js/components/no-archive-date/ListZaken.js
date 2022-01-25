import React, {useContext} from 'react';
import { useImmerReducer } from 'use-immer';
import useAsync from 'react-use/esm/useAsync';
import PropTypes from 'prop-types';

import {get} from '../../utils/api';
import {ZakenTable} from '../destruction-list-create/zaken-table';
import ErrorMessage from '../ErrorMessage';
import {Input} from '../../forms/inputs';
import {ZaaktypeSelect} from '../destruction-list-create/zaaktype-select';
import {UrlsContext} from '../context';
import ExportButton from './ExportButton';


const INITIAL_STATE = {
    zaken: [],
    checkboxes: {},
    filters: {
        identificatie: '',
        zaaktypen: []
    },
    error: null,
    isLoaded: false,
};


const reducer = (draft, action) => {
    switch (action.type) {
        case 'ZAKEN_LOADED': {
            const zaken = action.payload;
            draft.zaken = zaken;

            // Object with items:  zaak.url: bool which keeps track of which zaak have been selected
            draft.checkboxes = zaken.filter(zaak => zaak.available).reduce((result, zaak) => {
                return {...result, [zaak.url]: false};
            }, {});

            const uniqueBronorganisaties = new Set(zaken.map((zaak) => zaak.bronorganisatie));
            draft.bronorganisaties = Array.from(uniqueBronorganisaties);

            draft.isLoaded = true;
            break;
        }
        case 'SET_ERROR': {
            draft.isLoaded = true;
            draft.error = action.payload;
            break;
        }
        case 'START_FILTERING': {
            draft.isLoaded = false;

            const updatedFilters = action.payload;
            draft.filters = {
                ...draft.filters,
                ...updatedFilters
            };
            break;
        }
        case 'FINISHED_FILTERING': {
            const zaken = action.payload;
            draft.zaken = zaken;
            // Object with items:  zaak.url: bool which keeps track of which zaak have been selected
            draft.checkboxes = zaken.filter(zaak => zaak.available).reduce((result, zaak) => {
                return {...result, [zaak.url]: false};
            }, {});
            draft.isLoaded = true;
            break;
        }
        case 'UPDATE_CHECKBOXES': {
            draft.checkboxes = action.payload;
            break;
        }
        case 'TOGGLE_MODAL': {
            draft.modalIsOpen = action.payload;
            break;
        }
        default: {
          throw new Error(`Unknown action ${action.type}`);
        }
    }
};


const fetchZaken = async (path, filters) => {
    let searchUrl = new URL(window.location.href);
    searchUrl.pathname = path;

    let queryParams = {
        'archiefactiedatum__isnull': true,
        'einddatum__isnull': false,
        'sort_by_zaaktype': true
    };
    if (filters.zaaktypen.length) queryParams['zaaktype__in'] = filters.zaaktypen;
    if (!!filters.identificatie) queryParams['identificatie'] = filters.identificatie;

    const urlSearchParams = new URLSearchParams(queryParams);

    for (const [paramKey, paramValue] of urlSearchParams.entries()) {
        searchUrl.searchParams.set(paramKey, paramValue);
    }

    return await get(searchUrl);
};



const ListZaken = ({zakenUrl, zaaktypen}) => {
    const [state, dispatch] = useImmerReducer(reducer, INITIAL_STATE);

    const urlContext = useContext(UrlsContext);
    const exportZakenUrl = urlContext.exportZakenUrl;

    useAsync(async () => {
        const response = await get(zakenUrl, {
            'archiefactiedatum__isnull': true,
            'einddatum__isnull': false,
            'sort_by_zaaktype': true
        });

        if (!response.ok) {
            dispatch({type: 'SET_ERROR', payload: response.data});
            return;
        }

        dispatch({type: 'ZAKEN_LOADED', payload: response.data.zaken});
    }, []);

    const onFiltersChange = async (updatedFilters) => {
        dispatch({type: 'START_FILTERING', payload: updatedFilters});

        const filters = {
            ...state.filters,
            ...updatedFilters
        };

        const response = await fetchZaken(zakenUrl, filters);

        if (!response.ok) {
            dispatch({type: 'SET_ERROR', payload: response.data});
            return;
        }

        dispatch({type: 'FINISHED_FILTERING', payload: response.data.zaken});
    };

    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">Zaken zonder archiefactiedatum</h1>
                <nav className="destruction-create__nav">
                    <ExportButton exportZakenUrl={exportZakenUrl} checkboxes={state.checkboxes}/>
                </nav>
            </header>
            <div className="destruction-create__content">
                <aside className="destruction-create__filters filter-group">
                    <h2 className="section-title section-title--highlight">Filters</h2>
                    <div className="filter-group__item">
                        <label htmlFor={"id_zaaktypen"}>Zaak identificatie</label>
                        <div className="zaak-search-field">
                            <i className="material-icons zaak-search-field__icon">search</i>
                            <Input
                                type="text"
                                name="zaak-identificatie"
                                id="id_zaak-identificatie"
                                onChange={(event) => onFiltersChange({identificatie: event.target.value})}
                            />
                        </div>
                    </div>
                    <div className="filter-group__item">
                        <label htmlFor={"id_zaaktypen"}>Zaaktypen</label>
                        <ZaaktypeSelect
                            zaaktypen={zaaktypen}
                            selectedZaaktypen={state.filters.zaaktypen}
                            setSelectedZaaktypen={
                                (selectedZaaktypen) => onFiltersChange({zaaktypen: selectedZaaktypen})
                            }
                        />
                    </div>
                </aside>
                <section className="destruction-create__zaken">
                    <h2 className="section-title section-title--highlight">Zaakdossiers</h2>
                    <div className="destruction-create__explanation">
                        De zaken in deze tabel zijn gesloten (ze hebben een einddatum)
                        maar ze hebben geen archiefactiedatum.
                    </div>
                    {
                        !state.error
                        ? (<ZakenTable
                            zaken={state.zaken}
                            isLoaded={state.isLoaded}
                            error={state.error}
                            checkboxes={state.checkboxes}
                            setCheckboxes={(checkboxes) => dispatch({type: 'UPDATE_CHECKBOXES', payload: checkboxes})}
                            canUpdateZaak={true}
                        />)
                        : <ErrorMessage />
                    }
                </section>
            </div>
        </>
    );
};


ListZaken.propTypes = {
    zakenUrl: PropTypes.string.isRequired,
    zaaktypen: PropTypes.arrayOf(PropTypes.array)
};


export default ListZaken;
