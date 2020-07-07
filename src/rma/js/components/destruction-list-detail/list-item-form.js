import React, {useContext} from "react";

import {HiddenInput} from "../../forms/inputs";
import {FormsetConfigContext} from "./context";


const ListItemForm = ({ index, data }) => {
    const formsetConfig = useContext(FormsetConfigContext);
    const { list_item_id, zaak }  = data;

    const prefix = formsetConfig.prefix;
    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    return (
        <tr>
            <td className="table__hidden">
                <HiddenInput
                    id={id_prefix("id")}
                    name={name_prefix("id")}
                    value={list_item_id}
                />
            </td>
            <td>{ zaak.identificatie }</td>
            <td>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</td>
            <td>{ zaak.omschrijving }</td>
            <td>some status</td>
            <td className="table__hidden">

            </td>
        </tr>
    );
};


export { ListItemForm };
