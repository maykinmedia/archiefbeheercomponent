import React, { useState, useContext } from "react";

import { HiddenInput } from "../../forms/inputs";
import { ConstantsContext, SuggestionContext } from "./context";
import { ZaakDetailModal } from "./zaak-detail-modal";


const ReviewItemForm = ({ index, data }) => {
    const { list_item_id, zaak }  = data;
    const { formsetConfig, zaakDetailPermission } = useContext(ConstantsContext);
    const { suggestions } = useContext(SuggestionContext);

    const prefix = formsetConfig.prefix;
    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    const [ comment, setComment ] = useState("");
    const suggestion = suggestions[index];
    const disabled = !!suggestion;

    const actionIcon = (suggestion === "remove" ? "clear": (suggestion === "change_and_remove" ? "create" : "done"));

    // modal
    const canOpen = zaakDetailPermission === "True";
    const [modalIsOpen, setIsOpen] = React.useState(false);
    const openModal = () => {
        if (canOpen) {
            setIsOpen(true);
        }
    };

    return (
        <>
            <tr
                onClick={openModal}
                className={"review-item" + (disabled ? " review-item--disabled" : "") + (canOpen ? " review-item--clickable" : "")}
            >
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
                    <i className="material-icons">{actionIcon}</i>
                    <HiddenInput
                        id={id_prefix("suggestion")}
                        name={name_prefix("suggestion")}
                        value={suggestion}
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
                index={index}
                comment={comment}
                setComment={setComment}
            />
        </>
    );
};


export { ReviewItemForm };