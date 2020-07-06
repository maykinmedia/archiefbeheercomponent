import React, {useEffect, useState} from "react";

import { DateInput } from "./inputs";
import { ZakenTable } from "./zaken-table";
import { CreateModal} from "./create-modal";
import { ZaaktypeSelect} from "./zaaktype-select";
import { countObjectKeys } from "../../utils";


function getFullUrl(url, filters) {
    const query = Object.keys(filters).filter(k=>filters[k]).map(k => `${k}=${filters[k]}`).join('&');
    return `${url}?${query}`;
}


const DestructionForm = ({ zaaktypen, reviewers, zakenUrl, url, csrftoken }) => {

    //filters
    const [selectedZaaktypen, setSelectedZaaktypen] = useState([]);
    const [selectedStartdatum, setSelectedStartdatum] = useState(null);
    const filters = {
        zaaktypen: selectedZaaktypen,
        startdatum: selectedStartdatum,
    };

    //load zaken
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [zaken, setZaken] = useState([]);

    // checkboxes
    const [checkboxes, setCheckboxes] = useState({});
    const selectedCount = countObjectKeys(checkboxes);

    // modal
    const [modalIsOpen, setIsOpen] = React.useState(false);
    const openModal = () => setIsOpen(true);

    // fetch zaken
    useEffect(() => {
        const fullUrl = getFullUrl(zakenUrl, filters);
        window.fetch(fullUrl)
            .then(res => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setZaken(result.zaken);

                    // refresh checkboxes and deselect them
                    const refreshedCheckboxes = result.zaken.reduce((result, zaak) => {
                            return {...result, [zaak.url]: false};
                        }, {});
                    setCheckboxes(refreshedCheckboxes);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
    }, [selectedZaaktypen, selectedStartdatum]);


    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">Vernietigingslijst opstellen</h1>
                <nav className="title destruction-create__nav">
                    <button
                        type="button"
                        className="btn"
                        onClick={openModal}
                        disabled={!selectedCount}
                    >{selectedCount} zaken geselecteerd
                    </button>
                </nav>
            </header>
            <div className="destruction-create__content">
                <aside className="destruction-create__filters content-panel filter-group">
                    <h2 className="section-title section-title--highlight">Filters</h2>
                    <div className="filter-group__item">
                        <label htmlFor={"id_zaaktypen"}>Zaaktypen</label>
                        <ZaaktypeSelect
                            zaaktypen={zaaktypen}
                            selectedZaaktypen={selectedZaaktypen}
                            setSelectedZaaktypen={setSelectedZaaktypen}
                        />
                    </div>
                    <div className="filter-group__item">
                        <label htmlFor={"id_startdatum"}>Startdatum</label>
                        <DateInput
                            name={"startdatum"}
                            id={"id_startdatum"}
                            onBlur={(e) => {
                                const eventStartdatum = e.target.value;
                                if (eventStartdatum !== selectedStartdatum ) {
                                    setSelectedStartdatum(eventStartdatum);
                                }
                            }}
                        />
                    </div>

                </aside>

                <section className="destruction-create__zaken content-panel">
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
