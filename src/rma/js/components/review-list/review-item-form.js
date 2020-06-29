import React, { useEffect, useState, useContext } from "react";

import { HiddenInput } from "../../forms/inputs";
import { SelectInput } from "../../forms/select";
import { ConstantsContext } from "./context";
import { ZaakDetailModal } from "./zaak-detail-modal";
import {CreateModal} from "../destruction-list/create-modal";


const ITEM_SUGGESTIONS = [
    ["", "Approve"],
    ["remove", "Remove"],
    ["change_and_remove", "Change and remove"]
];


const ReviewItemForm = ({ index, data }) => {
    const { list_item_id, zaak }  = data;
    const { prefix } = useContext(ConstantsContext);

    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    const [ suggestion, setSuggestion ] = useState("");
    const [ comment, setComment ] = useState("");
    const disabled = !!suggestion;
    console.log("suggestion=", suggestion);
    console.log("disabled=", disabled);

    // modal
    const [modalIsOpen, setIsOpen] = React.useState(false);
    const openModal = () => setIsOpen(true);

    return (
        <>
            <tr onClick={openModal} className={"review-item" + (disabled ? " review-item--disabled" : "")}>
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
                        selected={suggestion}
                        choices={ITEM_SUGGESTIONS}
                        disabled={true}
                    />
                </td>
                <td className="table__hidden">
                    <HiddenInput
                        id={id_prefix("text")}
                        name={name_prefix("text")}
                        value={comment}
                    />
                </td>
            </tr>

            <ZaakDetailModal
                modalIsOpen={modalIsOpen}
                setIsOpen={setIsOpen}
                zaak={zaak}
                setSuggestion={setSuggestion}
                comment={comment}
                setComment={setComment}
            />
        </>
    );
};


export { ReviewItemForm };
