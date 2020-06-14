import React from "react";
import { SelectInput } from "./select";
import { DateInput} from "./inputs";
import { ZakenTable } from "./zaken-table";

function DestructionForm(props) {
    const { zaaktypen, zakenUrl } = props;

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
                    />
                </div>
                <div className="filter-group__item">
                    <label htmlFor={"id_startdatum"}>Startdatum</label>
                    <DateInput
                        name={"startdatum"}
                        id={"id_startdatum"}
                    />
                </div>
                <div className="filter-group__item">
                    <label htmlFor={"id_einddatum"}>Einddatum</label>
                    <DateInput
                        name={"einddatum"}
                        id={"id_einddatum"}
                    />
                </div>
            </aside>

            <section className="destruction-create__zaken content-panel">
                <h2 className="section-title section-title--highlight">Zaken</h2>
                <ZakenTable url={zakenUrl}/>
            </section>
        </>

    );
}

export {DestructionForm};
