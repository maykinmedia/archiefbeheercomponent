import React, {useEffect, useState} from "react";
import Modal from 'react-modal';
import { SelectInput } from "./select";
import { DateInput, TextInput} from "./inputs";
import { ZakenTable } from "./zaken-table";


function getFullUrl(url, filters) {
    const query = Object.keys(filters).filter(k=>filters[k]).map(k => `${k}=${filters[k]}`).join('&');
    return `${url}?${query}`;
}


function DestructionForm(props) {
    const { zaaktypen, zakenUrl } = props;

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
    console.log("checkboxes=", checkboxes);
    const selectedCount = Object.keys(checkboxes).reduce(
        (acc, key) => checkboxes[key] ? acc + 1 : acc,
    0);

    // modal
    const [modalIsOpen,setIsOpen] = React.useState(false);
    const openModal = () => setIsOpen(true);
    const closeModal = () => setIsOpen(false);

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
                        <SelectInput
                            choices={zaaktypen}
                            name={"zaaktypen"}
                            id={"id_zaaktypen"}
                            multiple={true}
                            classes="filter-group__select"
                            onChange={(zaaktypen) => setSelectedZaaktypen(zaaktypen)}
                            size="10"
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

            <Modal isOpen={modalIsOpen} className="modal">
                <button onClick={closeModal} className="modal__close btn">&times;</button>
                <form method="post" enctype="multipart/form-data" action="/destruction/record-managers/add">
                    <section className="filter-group">
                        <h1 className="title modal__title">Vernietigingslijst starten - {selectedCount} zaken</h1>
                        <div className="filter-group__item">
                            <label htmlFor={"id_name"}>Naam</label>
                            <TextInput
                                id={"id_name"}
                                name={"name"}
                            />
                        </div>
                    </section>
                    <button type="submit" className="btn">Bevestig</button>
                </form>

            </Modal>
        </>
    );
}

export {DestructionForm};
