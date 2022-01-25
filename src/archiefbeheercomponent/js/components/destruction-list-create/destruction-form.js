import React from 'react';
import { useImmerReducer } from 'use-immer';
import useAsync from 'react-use/esm/useAsync';

import { ZakenTable } from './zaken-table';
import { CreateModal} from './create-modal';
import { ZaaktypeSelect} from './zaaktype-select';
import { countObjectKeys } from '../../utils';
import {get} from '../../utils/api';
import BronorganisatieSelect from './BronorganisatieSelect';


const INITIAL_STATE = {
    filters: {
        zaaktypen: [],
        bronorganisaties: [],
    },
    bronorganisaties: [],
    checkboxes: {},
    error: null,
    isLoaded: false,
    zaken: [],
    modalIsOpen: false,
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


const fetchZaken = async (path, filters, currentDate) => {
    let searchUrl = new URL(window.location.href);
    searchUrl.pathname = path;

    let queryParams = {
        'archiefnominatie': 'vernietigen',
        'archiefactiedatum__lt': currentDate,
        'ordering': 'registratiedatum,startdatum,identificatie'
    };
    if (filters.zaaktypen.length) queryParams['zaaktype__in'] = filters.zaaktypen;
    if (filters.bronorganisaties.length) queryParams['bronorganisatie__in'] = filters.bronorganisaties;

    const urlSearchParams = new URLSearchParams(queryParams);

    for (const [paramKey, paramValue] of urlSearchParams.entries()) {
        searchUrl.searchParams.set(paramKey, paramValue);
    }

    return await get(searchUrl);
};


const DestructionForm = ({ zaaktypen, reviewers, zakenUrl, url, currentDate, csrftoken }) => {
    const [state, dispatch] = useImmerReducer(reducer, INITIAL_STATE);

    const selectedCount = countObjectKeys(state.checkboxes);

    useAsync(async () => {
        const response = await get(zakenUrl, {
            'archiefnominatie': 'vernietigen',
            'archiefactiedatum__lt': currentDate,
            'ordering': 'registratiedatum,startdatum,identificatie'
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

        const response = await fetchZaken(zakenUrl, filters, currentDate);

        if (!response.ok) {
            dispatch({type: 'SET_ERROR', payload: response.data});
            return;
        }

        dispatch({type: 'FINISHED_FILTERING', payload: response.data.zaken});
    };

    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">Vernietigingslijst opstellen</h1>
                <nav className="destruction-create__nav">
                    <button
                        type="button"
                        className="btn"
                        onClick={() => dispatch({type: 'TOGGLE_MODAL', payload: true})}
                        disabled={!selectedCount}
                    >Aanmaken</button>
                    <div>{selectedCount} zaken geselecteerd</div>
                </nav>
            </header>
            <div className="destruction-create__content">
                <aside className="destruction-create__filters filter-group">
                    <h2 className="section-title section-title--highlight">Filters</h2>
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
                    <div className="filter-group__item">
                        <label htmlFor={"id_bronorganisaties"}>Bronorganisatie</label>
                        <BronorganisatieSelect
                            bronorganisaties={state.bronorganisaties}
                            selectedBronorganisaties={state.filters.bronorganisaties}
                            onChange={
                                (selectedBronorganisaties) => onFiltersChange(
                                    {bronorganisaties: selectedBronorganisaties}
                                )
                            }
                        />
                    </div>
                </aside>

                <section className="destruction-create__zaken">
                    <h2 className="section-title section-title--highlight">Zaakdossiers</h2>
                    <div className="destruction-create__explanation">
                        De zaken in deze tabel hebben de archiefnominatie 'vernietigen' en
                        de archiefactiedatum is voor vandaag.
                    </div>
                    <ZakenTable
                        zaken={state.zaken}
                        isLoaded={state.isLoaded}
                        error={state.error}
                        checkboxes={state.checkboxes}
                        setCheckboxes={(checkboxes) => dispatch({type: 'UPDATE_CHECKBOXES', payload: checkboxes})}
                    />
                </section>
            </div>

            <CreateModal
                zaken={state.zaken}
                checkboxes={state.checkboxes}
                modalIsOpen={state.modalIsOpen}
                setIsOpen={(isOpen) => dispatch({type: 'TOGGLE_MODAL', payload: isOpen})}
                reviewers={reviewers}
                url={url}
                csrftoken={csrftoken}
            />

        </>
    );
}

export { DestructionForm };
