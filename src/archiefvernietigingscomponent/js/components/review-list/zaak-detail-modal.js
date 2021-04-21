import React, { useState, useContext, useEffect } from "react";
import Modal from 'react-modal';
import axios from "axios";

import {ConstantsContext, SuggestionContext} from "./context";
import {TextInput} from "../../forms/inputs";


const ZaakDetailModal = ({ modalIsOpen, setIsOpen, zaak, index, comment, setComment}) => {

    const { suggestions, setSuggestions } = useContext(SuggestionContext);

    const closeModal = () => setIsOpen(false);
    const suggestClose = (value) => {
        const newSuggestions = [...suggestions];
        newSuggestions[index] = value;
        setSuggestions(newSuggestions);

        closeModal();
    };

    return (
        <Modal isOpen={modalIsOpen} className="modal" bodyOpenClassName="modal-background__open">
            <article className="zaak-detail">
                <button onClick={closeModal} className="modal__close btn">&times;</button>
                <header className="zaak-detail__header">
                    <h1 className="title modal__title">Beoordeel de zaak</h1>
                </header>
                {zaak.zac_link !== null &&
                    <div className="zaak-detail__link">
                        Zaak:&nbsp;
                        <a
                            title="Open de geconfigureerde externe applicatie voor het bekijken van de zaak."
                            target="_blank"
                            href={zaak.zac_link}>
                            {zaak.identificatie}
                            <span className="material-icons">launch</span>
                        </a>
                    </div>
                }
                    <div className="zaak-detail__comment">
                        <label htmlFor="id_comment">Opmerkingen:</label>
                        <TextInput
                            id="id_comment"
                            name="comment"
                            initial={comment}
                            onChange={(event) => setComment(event.target.value)}
                        />
                    </div>

                    <div className="modal__buttons">
                        <button
                            type="button"
                            className="btn"
                            onClick={(e) => suggestClose("change_and_remove")}
                        >Aanpassen
                        </button>
                        <button
                            type="button"
                            className="btn"
                            onClick={(e) => suggestClose("remove")}
                        >Uitzonderen
                        </button>
                        <button
                            type="button"
                            className="btn"
                            onClick={(e) => suggestClose("")}
                        >Akkoord
                        </button>
                    </div>
            </article>

        </Modal>
    );
}

export { ZaakDetailModal };
