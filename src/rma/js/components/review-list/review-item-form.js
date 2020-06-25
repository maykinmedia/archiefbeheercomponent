import React, { useEffect, useState } from "react";
import { TextInput } from "../../forms/inputs";


const ReviewItemForm = ({ index, data }) => {
    const { list_item_id, zaak }  = data;

    return (
        <tr>
            <td>{ zaak.identificatie }</td>
            <td>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</td>
            <td>{ zaak.omschrijving }</td>
            <td>approve</td>
        </tr>
    );
};


export { ReviewItemForm };
