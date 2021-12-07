import React, { useState } from 'react';
import { CheckboxInput } from "../../forms/inputs";
import { Loader } from '../loader';
import ErrorMessage from '../ErrorMessage';
import ZaakRecord from "../no-archive-date/ZaakRecord";


function ZakenTable({ zaken, isLoaded, error, checkboxes, setCheckboxes }) {
    const [selectAll, setSelectAll] = useState(false);

    if (error) {
        return <ErrorMessage />;
    }

    if (!isLoaded) {
        return <Loader />;
    }

    return (
        <table className="table">
            <thead>
                <tr>
                    <th className="table__header row-box">
                        <CheckboxInput
                          checked={selectAll}
                          name="selectAll"
                          onChange={(e) => {
                              const tick = !selectAll;
                              setSelectAll(tick);
                              const selectedCheckboxes = {
                                  ...Object.keys(checkboxes).reduce(
                                      (result, key) => ({...result, [key]: tick}),
                                      {}
                                  )
                              };
                              setCheckboxes(selectedCheckboxes);
                          }}
                      /></th>
                    <th className="table__header row-id">Identificatie</th>
                    <th className="table__header row-zaaktype">Zaaktype</th>
                    <th className="table__header row-omschrijving" title="Zaak omschrijving">Omschrijving</th>
                    <th className="table__header row-looptijd">Looptijd</th>
                    <th className="table__header row-vo" title="Verantwoordelijke organisatie">VO</th>
                    <th className="table__header row-rt">Resultaattype</th>
                    <th className="table__header row-termijn" title="Archiefactietermijn">Bewaartermijn</th>
                    <th className="table__header row-vcs" title="Vernietigings-categorie selectielijst">VCS</th>
                    <th className="table__header row-relaties" title="Relaties met andere zaken?">Relaties?</th>
                </tr>
            </thead>
            <tbody>
                {zaken.map((zaak, key) => (
                    <ZaakRecord
                        key={key}
                        zaak={zaak}
                        isChecked={checkboxes[zaak.url] || false}
                        onCheckboxUpdate={(e) => {
                            const isChecked = !checkboxes[zaak.url];
                            setCheckboxes({...checkboxes, [zaak.url]: isChecked});
                            if (!isChecked) {
                              setSelectAll(false);
                            }
                        }}
                    />
                ))}

            </tbody>
        </table>
    );
}

export { ZakenTable };
