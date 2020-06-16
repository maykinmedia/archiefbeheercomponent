import React, {useState} from 'react';
import { CheckboxInput} from "./inputs";


function displayZaaktype (zaaktype) {
    return `${zaaktype.omschrijving} (${zaaktype.versiedatum}}`;
}


function ZakenTable(props) {
    const { zaken, isLoaded, error, checkboxes, setCheckboxes } = props;

    const [selectAll, setSelectAll] = useState(false);

    if (error) {
        return <div>Error in fetching zaken: {error.message}</div>;
    }

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <table className="table">
            <thead>
                <tr>
                    <th className="table__header">
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
                    <th className="table__header">Zaaktype</th>
                    <th className="table__header">Omschrijving</th>
                    <th className="table__header">Startdatum</th>
                    <th className="table__header">Einddatum</th>
                    <th className="table__header">Archiefactiedatum</th>
                </tr>
            </thead>
            <tbody>
                {zaken.map(zaak => (
                  <tr key={zaak.url}>
                      <td>
                          <CheckboxInput
                              checked={checkboxes[zaak.url]}
                              name={zaak.url}
                              onChange={(e) => {
                                  const isChecked = !checkboxes[zaak.url];
                                  setCheckboxes({...checkboxes, [zaak.url]: isChecked});
                                  if (!isChecked) {
                                      setSelectAll(false);
                                  }
                              }}
                          />
                      </td>
                      <td>{displayZaaktype(zaak.zaaktype)}</td>
                      <td>{zaak.omschrijving}</td>
                      <td>{zaak.startdatum}</td>
                      <td>{zaak.einddatum}</td>
                      <td>{zaak.archiefactiedatum}</td>
                  </tr>
                ))}

            </tbody>
        </table>
    );
}

export { ZakenTable };