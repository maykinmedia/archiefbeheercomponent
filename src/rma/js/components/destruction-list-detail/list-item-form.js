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

    // archive inputs
    const [archiefnominatie, setArchiefnominatie] = useState("");

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
                <td>{ listItem.status }</td>
                <td className="table__hidden">

                </td>
            </tr>
            <ListItemModal
                modalIsOpen={modalIsOpen}
                setIsOpen={setIsOpen}
                listItem={listItem}
                zaak={zaak}
                archiefnominatie={archiefnominatie}
                setArchiefnominatie={setArchiefnominatie}
            />
        </>
    );
};


export { ListItemForm };
