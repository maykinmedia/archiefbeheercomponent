import React, {useEffect, useState} from "react";
import { SelectInput } from "./select";
import { DateInput} from "./inputs";
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
                <h1 className="title destruction-create__title">Create new destruction list</h1>
                <nav className="title destruction-create__nav">
                    <button type="button" className="btn">{selectedCount} zaken selected</button>
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
                    <h2 className="section-title section-title--highlight">Zaken</h2>
                    <ZakenTable
                        zaken={zaken}
                        isLoaded={isLoaded}
                        error={error}
                        checkboxes={checkboxes}
                        setCheckboxes={setCheckboxes}
                    />
                </section>
            </div>
        </>
    );
}

export {DestructionForm};
