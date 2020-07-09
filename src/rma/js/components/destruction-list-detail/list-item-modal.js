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


const ListItemModal = ({modalIsOpen, setIsOpen, listItem, zaak, setAction, archiveInputs}) => {
    const {archiefnominatie, setArchiefnominatie, archiefactiedatum, setArchiefactiedatum} = archiveInputs;
    const closeModal = () => setIsOpen(false);

    const title = SUGGESTION_TO_TITLE[listItem.review_suggestion] || "No";
    const currentAction = (
        archiefnominatie !== zaak.archiefnominatie || archiefactiedatum !== zaak.archiefactiedatum
            ? "change_and_remove"
            : "remove"
    );

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <article className="list-item-modal">
                <button onClick={closeModal} className="modal__close btn">&times;</button>
                <h1 className="title modal__title">{zaak.identificatie}</h1>

                <div className="modal__section">
                    <section className="content-panel modal__item">
                        <h2 className="section-title section-title--highlight">Remarks</h2>

                        <p>
                            { listItem.review_text ? listItem.review_text : "No comment"}
                        </p>
                    </section>
                    <section className="content-panel modal__item">
                        <h2 className="section-title section-title--highlight">Suggestion: { title }</h2>

                        <div className="list-item-modal__archiefnominatie">
                        <label>Archiefnominatie
                            <RadioSelect
                                name="archiefnominatie"
                                choices={ARCHIEFNOMINATIE_CHOICES}
                                initialValue={archiefnominatie}
                                onChange={(e) => setArchiefnominatie(e.target.value)}
                            />
                        </label>
                        </div>

                        <div className="list-item-modal__archiefactiedatum">
                            <label>Archiefactiedatum
                                <DateInput
                                    name="archiefactiedatum"
                                    initial={archiefactiedatum}
                                    onChange={(e) => setArchiefactiedatum(e.target.value)}
                                />
                            </label>
                        </div>
                    </section>
                </div>

                <div className="modal__buttons">
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

