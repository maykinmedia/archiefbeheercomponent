import React from 'react';

import {CheckboxInput} from '../../forms/inputs';


const displayZaaktype = (zaaktype) => {
    return (
        <span className="zaak-record__zaaktype" title={`versie ${zaaktype.versiedatum}`}>
            {zaaktype.omschrijving}
        </span>
    );
};


const ZaakRecord = ({zaak, canUpdate, isChecked, onCheckboxUpdate}) => {
    const canUpdateZaak = canUpdate && zaak.available;

    const onZaakClick = () => {
        if (!canUpdateZaak) return;

        let currentLocation = new URL(window.location)
        currentLocation.pathname = '/vernietigen/lijsten/update-zaak-archive-details/';
        currentLocation.searchParams.set('url', zaak.url);
        if (zaak.archiefactiedatum) currentLocation.searchParams.set('archiefactiedatum', zaak.archiefactiedatum);
        if (zaak.archiefnominatie) currentLocation.searchParams.set('archiefnominatie', zaak.archiefnominatie);

        window.location.href = currentLocation;
    };

    return (
        <>
            <tr
              key={zaak.url}
              className={"zaak-record" + (!zaak.available ? " zaak-record--disabled" : "")}
            >
                <td>
                  <CheckboxInput
                      checked={isChecked}
                      name={zaak.url}
                      onChange={onCheckboxUpdate}
                      disabled={!zaak.available}
                  />
                </td>
                <td>
                    {
                        canUpdateZaak
                        ? (<a
                                className="link"
                                onClick={onZaakClick}
                                title="Archiefgegevens aanpassen"
                                href="#"
                            >{ zaak.identificatie }</a>)
                        : <div>{ zaak.identificatie }</div>
                    }
                </td>
                <td>{displayZaaktype(zaak.zaaktype)}</td>
                <td>{zaak.omschrijving}</td>
                <td>{ zaak.looptijd }</td>
                <td>{ zaak.verantwoordelijkeOrganisatie }</td>
                <td>{ zaak.resultaat ? zaak.resultaat.resultaattype.omschrijving : '-' }</td>
                <td>{ zaak.resultaat ? zaak.resultaat.resultaattype.archiefactietermijn : '-'}</td>
                <td>{ zaak.zaaktype.processtype ? zaak.zaaktype.processtype.nummer : "-" }</td>
                <td>{ zaak.relevanteAndereZaken.length > 0 ? "Ja" : "Nee" }</td>
            </tr>
        </>
    );
};

export default ZaakRecord;
