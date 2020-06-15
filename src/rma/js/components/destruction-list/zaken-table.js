import React, {useEffect, useState} from 'react';
import { CheckboxInput} from "./inputs";


function displayZaaktype (zaaktype) {
    return `${zaaktype.omschrijving} (${zaaktype.versiedatum}}`;
}

function getFullUrl(url, filters) {
    const query = Object.keys(filters).filter(k=>filters[k]).map(k => `${k}=${filters[k]}`).join('&');
    return `${url}?${query}`;
}

function ZakenTable(props) {
    const { url, filters } = props;

    //load zaken
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [zaken, setZaken] = useState([]);

    // checkboxes
    const [selectAll, setSelectAll] = useState(false);
    const [checkboxes, setCheckboxes] = useState({});
    console.log("checkboxes=", checkboxes);

    useEffect(() => {
        const fullUrl = getFullUrl(url, filters);
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
      }, [filters])

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
