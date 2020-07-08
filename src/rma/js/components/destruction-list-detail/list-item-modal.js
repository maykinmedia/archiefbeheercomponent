import React, {useContext, useState} from "react";
import Modal from 'react-modal';

import {DateInput} from "../../forms/inputs";
import {RadioSelect} from "../../forms/select";


const SUGGESTION_TO_TITLE = {
    "no": "No",
    "remove": "Remove",
    "change_and_remove": "Change and remove"
};

const ARCHIEFNOMINATIE_CHOICES = [
    ["blijvend_bewaren", "blijvend bewaren"],
    ["vernietigen", "vernietigen"]
];


const ListItemModal = ({modalIsOpen, setIsOpen, listItem, zaak, status, setStatus, archiveInputs}) => {
    const {archiefnominatie, setArchiefnominatie, archiefactiedatum, setArchiefactiedatum} = archiveInputs;
    const closeModal = () => setIsOpen(false);

    const title = SUGGESTION_TO_TITLE[listItem.review_suggestion || "no"];
    const button = (
        archiefnominatie !== zaak.archiefnominatie || archiefactiedatum !== zaak.archiefactiedatum
            ? "Change and remove"
            : "Remove"
    );

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <article>
                <button onClick={closeModal} className="modal__close btn">&times;</button>
                <h1 className="title modal__title">{zaak.identificatie}</h1>

                <div>
                    <section className="content-panel">
                        <h2 className="section-title section-title--highlight">Remarks</h2>

                        <p>
                            { listItem.review_text ? listItem.review_text : "No comment"}
                        </p>
                    </section>
                    <section className="content-panel">
                        <h2 className="section-title section-title--highlight">Suggestion: { title }</h2>

                        <label>Archiefnominatie
                            <RadioSelect
                                name="archiefnominatie"
                                choices={ARCHIEFNOMINATIE_CHOICES}
                                initialValue={archiefnominatie}
                                onChange={(e) => setArchiefnominatie(e.target.value)}
                            />
                        </label>

                        <label>Archiefactiedatum
                            <DateInput
                                name="archiefactiedatum"
                                initial={archiefactiedatum}
                                onChange={(e) => setArchiefactiedatum(e.target.value)}
                            />
                        </label>

                    </section>

                    <button
                        onClick={(e) => {
                            setStatus("remove");
                            closeModal();
                        }}
                        className="btn"
                    >{button}
                    </button>
                </div>
            </article>
        </Modal>
    );
};

export { ListItemModal };

