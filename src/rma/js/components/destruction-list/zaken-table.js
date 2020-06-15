import React, {useEffect, useState} from 'react';


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

    useEffect(() => {
        const fullUrl = getFullUrl(url, filters);
        console.log("full url=", fullUrl);
        window.fetch(fullUrl)
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
