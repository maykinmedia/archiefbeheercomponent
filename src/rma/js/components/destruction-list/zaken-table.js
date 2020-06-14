import React, {useEffect, useState} from 'react';


function ZakenTable(props) {
    const { url } = props;

    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [zaken, setZaken] = useState([]);

    const displayZaaktype = (zaaktype) => {
        return `${zaaktype.omschrijving} (${zaaktype.versiedatum}}`;
    };

    useEffect(() => {
        window.fetch(url)
            .then(res => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setZaken(result.zaken);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
      }, [])

    if (error) {
        return <div>Error in fetching zaken: {error.message}</div>;
    }

    return (
        <table className="table">
            <thead>
                <tr>
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
