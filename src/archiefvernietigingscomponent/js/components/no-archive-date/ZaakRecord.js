import React, {useContext} from 'react';

import {CheckboxInput} from '../../forms/inputs';
import {ArchiveUpdateUrlContext} from '../context';


const displayZaaktype = (zaaktype) => {
    return (
        <span className="zaak-record__zaaktype" title={`versie ${zaaktype.versiedatum}`}>
            {zaaktype.omschrijving}
        </span>
    );
};


const ZaakRecord = ({zaak, isChecked, onCheckboxUpdate}) => {
    const archiveUpdateUrl = useContext(ArchiveUpdateUrlContext);
    const canUpdateZaak = zaak.available;

    const getZaakUpdateUrl = (zaak) => {
        if (!canUpdateZaak) return '#';

        let currentLocation = new URL(window.location)
        currentLocation.pathname = archiveUpdateUrl;
        currentLocation.searchParams.set('url', zaak.url);
        return currentLocation.href;
    };

    return (
        <>
            <tr
              key={zaak.url}
              className={'zaak-record' + (!zaak.available ? ' zaak-record--disabled' : '')}
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
                                title="Archiefgegevens aanpassen"
                                href={getZaakUpdateUrl(zaak)}
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
                <td>{ zaak.zaaktype.processtype ? zaak.zaaktype.processtype.nummer : '-' }</td>
                <td>{ zaak.relevanteAndereZaken.length > 0 ? 'Ja' : 'Nee' }</td>
            </tr>
        </>
    );
};

export default ZaakRecord;
