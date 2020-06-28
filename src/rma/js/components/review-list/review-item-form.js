import React, { useEffect, useState } from "react";
import { TextInput, HiddenInput } from "../../forms/inputs";
import { SelectInput } from "../../forms/select";

const PREFIX = "item_reviews";

const ITEM_SUGGESTIONS = [
    ["", "Approve"],
    ["remove", "Remove"],
    ["change_and_remove", "Change and remove"]
];


const ReviewItemForm = ({ index, data }) => {
    const { list_item_id, zaak }  = data;

    const id_prefix = (field) => `id_${PREFIX}-${index}-${field}`;
    const name_prefix = (field) => `${PREFIX}-${index}-${field}`;

    const [ suggestion, setSuggestion ] = useState(ITEM_SUGGESTIONS.approve);

    return (
        <tr>
            <td className="table__hidden">
                <HiddenInput
                    id={id_prefix("destruction_list_item")}
                    name={name_prefix("destruction_list_item")}
                    value={list_item_id}
                />
            </td>
            <td>{ zaak.identificatie }</td>
            <td>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</td>
            <td>{ zaak.omschrijving }</td>
            <td>
                <SelectInput
                    id={id_prefix("suggestion")}
                    name={name_prefix("suggestion")}
                    initial={suggestion}
                    choices={ITEM_SUGGESTIONS}
                    // disabled={true}
                />
            </td>
        </tr>
    );
};


export { ReviewItemForm };
