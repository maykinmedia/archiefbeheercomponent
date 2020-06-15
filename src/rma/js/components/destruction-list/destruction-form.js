import React, { useState } from "react";
import { SelectInput } from "./select";
import { DateInput} from "./inputs";
import { ZakenTable } from "./zaken-table";

function DestructionForm(props) {
    const { zaaktypen, zakenUrl } = props;

    //filters
    const [selectedZaaktypen, setSelectedZaaktypen] = useState([]);
    const [selectedStartdatum, setSelectedStartdatum] = useState(null);
    const filters = {
        zaaktypen: selectedZaaktypen,
        startdatum: selectedStartdatum,
    };

    return (
        <>
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
                <ZakenTable url={zakenUrl} filters={filters}/>
            </section>
        </>
    );
}

export {DestructionForm};
