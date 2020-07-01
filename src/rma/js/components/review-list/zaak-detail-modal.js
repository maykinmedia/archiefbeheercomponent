import React, { useState, useContext, useEffect } from "react";
import Modal from 'react-modal';
import axios from "axios";

import {ConstantsContext, SuggestionContext} from "./context";
import {TextInput} from "../../forms/inputs";


const ZaakDetailModal = ({ modalIsOpen, setIsOpen, zaak, index, comment, setComment}) => {

    const { zaakDetailUrl } = useContext(ConstantsContext);
    const { suggestions, setSuggestions } = useContext(SuggestionContext);

    const closeModal = () => setIsOpen(false);
    const suggestClose = (value) => {
        const newSuggestions = [...suggestions];
        newSuggestions[index] = value;
        setSuggestions(newSuggestions);

        closeModal();
    };

    // load zaak detail
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [zaakDetail, setZaakDetail] = useState({});
    const {resultaat, documenten, besluiten} = zaakDetail;

    // fetch zaak details
    useEffect(() => {
        if (modalIsOpen && !isLoaded) {
            axios.get(zaakDetailUrl, {params: {zaak_url: zaak.url}})
                .then(
                    (result) => {
                        setIsLoaded(true);
                        setZaakDetail(result.data);
                    },
                    (error) => {
                        setIsLoaded(true);
                        setError(error);
                    }
                )
        }
    }, [modalIsOpen, isLoaded]);

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <article className="zaak-detail">
                <button onClick={closeModal} className="modal__close btn">&times;</button>
                <h1 className="title modal__title">{zaak.identificatie}</h1>
                <span>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</span>

                {error
                    ? <div>Error in fetching zaak details: {error.message}</div>
                    : !isLoaded
                        ? <div>Loading...</div>
                        : <>
                            <div className="zaak-detail__section">
                                <section className="content-panel zaak-detail__item">
                                    <h2 className="section-title section-title--highlight">Besluiten</h2>
                                    {!besluiten
                                        ? <span>The zaak doesn't have related besluiten</span>
                                        : <ul>
                                            { besluiten.map(
                                                (besluit) => <li key={besluit.url}>{ besluit.identificatie} </li>
                                            )}
                                        </ul>
                                    }

                                </section>
                                <section className="content-panel zaak-detail__item">
                                    <h2 className="section-title section-title--highlight">Resultaat</h2>
                                    {!resultaat
                                        ? <span>The zaak doesn't have a resultaat</span>
                                        : <span title={ resultaat.toelichting }>{ resultaat.resultaattype.omschrijving }</span>
                                    }
                                </section>
                            </div>
                            <section className="content-panel">
                                <h2 className="section-title section-title--highlight">Documenten</h2>
                                {!documenten
                                    ? <span>The zaak doesn't have related documenten</span>
                                    : <ul>
                                        { documenten.map(
                                            (document) => <li key={document.url}>{ document.identificatie }</li>
                                        )}
                                    </ul>
                                }
                            </section>

                            <div>
                                <label htmlFor="id_comment">Comment:</label>
                                <TextInput
                                    id="id_comment"
                                    name="comment"
                                    initial={comment}
                                    onChange={(event) => setComment(event.target.value)}
                                />
                            </div>

                            <div className="zaak-detail__buttons">
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

                        </>
                }
            </article>

        </Modal>
    );
}

export { ZaakDetailModal };
