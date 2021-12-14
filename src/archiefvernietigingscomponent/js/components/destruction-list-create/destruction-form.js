import React, {useEffect, useState} from 'react';

import {CheckboxInput, DateInput} from '../../forms/inputs';
import { ZakenTable } from './zaken-table';
import { CreateModal} from './create-modal';
import { ZaaktypeSelect} from './zaaktype-select';
import { countObjectKeys } from '../../utils';


function getSearchZakenUrl(path, filters, currentDate) {
    let searchUrl = new URL(window.location.href);
    searchUrl.pathname = path;

    let queryParams = {
        'archiefnominatie': 'vernietigen',
        'archiefactiedatum__lt': currentDate,
        'ordering': 'registratiedatum,startdatum,identificatie'
    };
    if (filters.zaaktypen.length) queryParams['zaaktype__in'] = filters.zaaktypen;
    if (filters.bronorganisaties.length) queryParams['bronorganisatie__in'] = filters.bronorganisaties;
    if (filters.startdatum) queryParams['startdatum__gte'] = filters.startdatum;

    const urlSearchParams = new URLSearchParams(queryParams);

    for (const [paramKey, paramValue] of urlSearchParams.entries()) {
        searchUrl.searchParams.set(paramKey, paramValue);
    }
    return searchUrl;
}


const DestructionForm = ({ zaaktypen, reviewers, zakenUrl, url, currentDate, csrftoken }) => {

    //filters
    const [selectedZaaktypen, setSelectedZaaktypen] = useState([]);
    const [selectedStartdatum, setSelectedStartdatum] = useState(null);
    const [selectedBronorganisatie, setSelectedBronorganisatie] = useState([]);
    const filters = {
        zaaktypen: selectedZaaktypen,
        startdatum: selectedStartdatum,
        bronorganisaties: selectedBronorganisatie,
    };

    //load zaken
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [zaken, setZaken] = useState([]);

    // Available bronorganisaties
    const [bronorganisaties, setBronorganisaties] = useState([]);

    // checkboxes
    const [checkboxes, setCheckboxes] = useState({});
    const selectedCount = countObjectKeys(checkboxes);

    // modal
    const [modalIsOpen, setIsOpen] = React.useState(false);
    const openModal = () => setIsOpen(true);

    // fetch zaken
    useEffect(() => {
        const fullUrl = getSearchZakenUrl(zakenUrl, filters, currentDate);
        window.fetch(fullUrl)
            .then(res => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setZaken(result.zaken);

                    // refresh checkboxes and deselect them
                    const refreshedCheckboxes = result.zaken.filter(zaak => zaak.available).reduce((result, zaak) => {
                            return {...result, [zaak.url]: false};
                        }, {});
                    setCheckboxes(refreshedCheckboxes);

                    // Should only get the available bronorganisaties once
                    if (bronorganisaties.length === 0) {
                        // Get all the unique values of the bronorganisatie
                        const uniqueBronorganisaties = new Set(result.zaken.map((zaak) => zaak.bronorganisatie));
                        setBronorganisaties(Array.from(uniqueBronorganisaties));
                    }
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            );
    }, [selectedZaaktypen, selectedStartdatum, selectedBronorganisatie]);

    const bronorganisatieCheckboxes = bronorganisaties.map((bronorganisatie, index) => {
        return (
            <label key={index}>
                <CheckboxInput
                    checked={selectedBronorganisatie.includes(bronorganisatie)}
                    name={bronorganisatie}
                    onChange={(e) => {
                        if (e.target.checked){
                            setSelectedBronorganisatie([...selectedBronorganisatie, bronorganisatie]);
                        } else {
                            setSelectedBronorganisatie(selectedBronorganisatie.filter((value) => {
                                return value !== bronorganisatie;
                            }));
                        }
                    }}
                />
                {bronorganisatie}
            </label>
        );
    })

    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">Vernietigingslijst opstellen</h1>
                <nav className="destruction-create__nav">
                    <button
                        type="button"
                        className="btn"
                        onClick={openModal}
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
                            selectedZaaktypen={selectedZaaktypen}
                            setSelectedZaaktypen={(selected) => {
                                setIsLoaded(false);
                                setSelectedZaaktypen(selected);
                            }}
                        />
                    </div>
                    <div className="filter-group__item">
                        <label htmlFor={"id_bronorganisaties"}>Bronorganisatie</label>
                        {bronorganisatieCheckboxes}
                    </div>
                    <div className="filter-group__item">
                        <label htmlFor={"id_startdatum"}>Startdatum</label>
                        <DateInput
                            name={"startdatum"}
                            id={"id_startdatum"}
                            onBlur={(e) => {
                                const eventStartdatum = e.target.value;
                                if (eventStartdatum !== selectedStartdatum ) {
                                    setIsLoaded(false);
                                    setSelectedStartdatum(eventStartdatum);
                                }
                            }}
                        />
                    </div>

                </aside>

                <section className="destruction-create__zaken">
                    <h2 className="section-title section-title--highlight">Zaakdossiers</h2>
                    <ZakenTable
                        zaken={zaken}
                        isLoaded={isLoaded}
                        error={error}
                        checkboxes={checkboxes}
                        setCheckboxes={setCheckboxes}
                    />
                </section>
            </div>

            <CreateModal
                zaken={zaken}
                checkboxes={checkboxes}
                modalIsOpen={modalIsOpen}
                setIsOpen={setIsOpen}
                reviewers={reviewers}
                url={url}
                csrftoken={csrftoken}
            />

        </>
    );
}

export { DestructionForm };
