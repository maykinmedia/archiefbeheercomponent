import React from 'react';
import { useImmerReducer } from 'use-immer';
import {FormattedMessage} from 'react-intl';
import useAsync from 'react-use/esm/useAsync';

import { ZakenTable } from './zaken-table';
import { CreateModal} from './create-modal';
import { ZaaktypeSelect} from './zaaktype-select';
import { countObjectKeys } from '../../utils';
import {get} from '../../utils/api';
import BronorganisatieSelect from './BronorganisatieSelect';
import {fetchZaken} from '../utils';


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


const DestructionForm = ({ zaaktypen, reviewers, zakenUrl, url, currentDate, csrftoken }) => {
    const [state, dispatch] = useImmerReducer(reducer, INITIAL_STATE);

    const queryParams = {
        'archiefnominatie': 'vernietigen',
        'archiefactiedatum__lt': currentDate,
        'ordering': 'registratiedatum,startdatum,identificatie'
    };
    const selectedCount = countObjectKeys(state.checkboxes);

    useAsync(async () => {
        const response = await get(zakenUrl, queryParams);

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

        const response = await fetchZaken(zakenUrl, filters, queryParams);

        if (!response.ok) {
            dispatch({type: 'SET_ERROR', payload: response.data});
            return;
        }

        dispatch({type: 'FINISHED_FILTERING', payload: response.data.zaken});
    };

    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">
                    <FormattedMessage
                        defaultMessage="Create destruction list"
                        description="Title create destruction list page"
                    />
                </h1>
                <nav className="destruction-create__nav">
                    <button
                        type="button"
                        className="btn"
                        onClick={() => dispatch({type: 'TOGGLE_MODAL', payload: true})}
                        disabled={!selectedCount}
                    >
                        <FormattedMessage defaultMessage="Create" description="Button 'create'" />
                    </button>
                    <div>
                        <FormattedMessage
                            description="How many cases selected"
                            defaultMessage="{numSelectedZaken, plural,
                                =0 {No cases selected}
                                one {1 case selected}
                                other {{numSelectedZaken} cases selected}
                            }"
                            values={{numSelectedZaken: selectedCount}}
                        />
                    </div>
                </nav>
            </header>
            <div className="destruction-create__content">
                <aside className="destruction-create__filters filter-group">
                    <h2 className="section-title section-title--highlight">Filters</h2>
                    <div className="filter-group__item">
                        <label htmlFor={"id_zaaktypen"}><FormattedMessage defaultMessage="Case types" description="Case types" /></label>
                        <ZaaktypeSelect
                            zaaktypen={zaaktypen}
                            selectedZaaktypen={state.filters.zaaktypen}
                            setSelectedZaaktypen={
                                (selectedZaaktypen) => onFiltersChange({zaaktypen: selectedZaaktypen})
                            }
                        />
                    </div>
                    <div className="filter-group__item">
                        <label htmlFor={"id_bronorganisaties"}><FormattedMessage defaultMessage="Source organisation" description="Source organisation" /></label>
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
                    <h2 className="section-title section-title--highlight"><FormattedMessage defaultMessage="Cases" description="Zaakdossiers" /></h2>
                    <div className="destruction-create__explanation">
                        <FormattedMessage
                            defaultMessage="The cases in this table have the archive nomination 'delete' and their archiving date is before today"
                            description="Describe which cases are shown"
                        />
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
