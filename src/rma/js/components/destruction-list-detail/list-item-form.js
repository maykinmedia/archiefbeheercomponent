import React, {useContext, useState} from "react";

import {HiddenInput} from "../../forms/inputs";
import {FormsetConfigContext} from "./context";
import {ListItemModal} from "./list-item-modal";


const ListItemForm = ({ index, data }) => {
    const formsetConfig = useContext(FormsetConfigContext);
    const { listItem, zaak }  = data;

    const prefix = formsetConfig.prefix;
    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    // modal
    const [modalIsOpen, setIsOpen] = useState(false);
    const openModal = () => setIsOpen(true);

    const [status, setStatus] = useState(listItem.status);
    // archive inputs
    const [archiefnominatie, setArchiefnominatie] = useState(zaak.archiefnominatie);
    const [archiefactiedatum, setArchiefactiedatum] = useState(zaak.archiefactiedatum);
    const archiveInputs = {archiefnominatie, setArchiefnominatie, archiefactiedatum, setArchiefactiedatum};

    return (
        <>
            <tr
                className="list-item list-item--clickable"
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
                <td>{ status }
                    <HiddenInput
                        id={id_prefix("status")}
                        name={name_prefix("status")}
                        value={status}
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
                status={status}
                setStatus={setStatus}
                archiveInputs={archiveInputs}
            />
        </>
    );
};


export { ListItemForm };
