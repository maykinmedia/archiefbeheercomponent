import React, { useState, useContext } from "react";

import { HiddenInput } from "../../forms/inputs";
import { ConstantsContext, SuggestionContext } from "./context";
import { ZaakDetailModal } from "./zaak-detail-modal";
import { ActionIcon } from "../../forms/action-icon";


const ReviewItemForm = ({ index, data }) => {
    const { listItem, zaak }  = data;
    const { formsetConfig, zaakDetailPermission } = useContext(ConstantsContext);
    const { suggestions } = useContext(SuggestionContext);

    const prefix = formsetConfig.prefix;
    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    const [ comment, setComment ] = useState("");
    const suggestion = suggestions[index];
    const disabled = !!suggestion;

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
                className={"list-item" + (disabled ? " list-item--disabled" : "") + (canOpen ? " list-item--clickable" : "")}
            >
                <td className="table__hidden">
                    <HiddenInput
                        id={id_prefix("destruction_list_item")}
                        name={name_prefix("destruction_list_item")}
                        value={listItem.id}
                    />
                </td>
                <td>{ zaak.identificatie }</td>
                <td>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</td>
                <td>{ zaak.omschrijving }</td>
                <td>{ zaak.looptijd }</td>
                <td>{ zaak.verantwoordelijkeOrganisatie }</td>
                <td>{ zaak.resultaattype.omschrijving }</td>
                <td>{ zaak.resultaattype.archiefactietermijn }</td>
                <td>{ zaak.zaaktype.selectielijstProcestype ? zaak.zaaktype.selectielijstProcestype.nummer : "-" }</td>
                <td>{ zaak.relevanteAndereZaken.length > 0 ? "Ja" : "Nee" }</td>
                <td>
                    <ActionIcon action={suggestion}/>
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
