import React, {useContext, useState} from "react";

import {HiddenInput} from "../../forms/inputs";
import {FormsetConfigContext, CanUpdateContext} from "./context";
import {ListItemModal} from "./list-item-modal";
import {ActionIcon} from "../../forms/action-icon";


const ListItemForm = ({ index, data }) => {
    const formsetConfig = useContext(FormsetConfigContext);
    const canUpdate = useContext(CanUpdateContext);
    const { listItem, zaak }  = data;

    const prefix = formsetConfig.prefix;
    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    // modal
    const [modalIsOpen, setIsOpen] = useState(false);
    const openModal = () => {
        if (canUpdate) {
            setIsOpen(true);
        }
    };

    const [action, setAction] = useState("");

    const getExtraClasses = () => {
        if (!canUpdate) {
            return "";
        }

        let classes = " list-item--clickable";

        if (action) {
            classes += " list-item--disabled";
        } else if (listItem.review_suggestion) {
            classes += " list-item--disabled";
        }

        return classes;
    };

    // archive inputs
    const [archiefnominatie, setArchiefnominatie] = useState(zaak.archiefnominatie);
    const [archiefactiedatum, setArchiefactiedatum] = useState(zaak.archiefactiedatum);
    const archiveInputs = {archiefnominatie, setArchiefnominatie, archiefactiedatum, setArchiefactiedatum};

    return (
        <>
            <tr
                className={"list-item" + getExtraClasses()}
                onClick={openModal}
            >
                <td className="table__hidden">
                    <HiddenInput
                        id={id_prefix("id")}
                        name={name_prefix("id")}
                        value={listItem.id}
                    />
                </td>
                <td>{ zaak.identificatie }</td>
                <td>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</td>
                <td>{ zaak.omschrijving }</td>
                <td>{ zaak.looptijd }</td>
                <td>{ zaak.verantwoordelijkeOrganisatie }</td>
                <td>{ zaak.resultaat ? zaak.resultaat.resultaattype.omschrijving : '-' }</td>
                <td>{ zaak.resultaat ? zaak.resultaat.resultaattype.archiefactietermijn : '-'}</td>
                <td>{ zaak.zaaktype.selectielijstProcestype ? zaak.zaaktype.selectielijstProcestype.nummer : "-" }</td>
                <td>{ zaak.relevanteAndereZaken.length > 0 ? "Ja" : "Nee" }</td>
                <td>{ listItem.status }</td>
                <td>
                    <ActionIcon action={action}/>
                    <HiddenInput
                        id={id_prefix("action")}
                        name={name_prefix("action")}
                        value={action}
                    />
                </td>
                <td className="table__hidden">
                    <HiddenInput
                        id={id_prefix("archiefnominatie")}
                        name={name_prefix("archiefnominatie")}
                        value={archiefnominatie}
                    />
                    <HiddenInput
                        id={id_prefix("archiefactiedatum")}
                        name={name_prefix("archiefactiedatum")}
                        value={archiefactiedatum}
                    />
                </td>
            </tr>
            <ListItemModal
                modalIsOpen={modalIsOpen}
                setIsOpen={setIsOpen}
                listItem={listItem}
                zaak={zaak}
                setAction={setAction}
                archiveInputs={archiveInputs}
            />
        </>
    );
};


export { ListItemForm };
