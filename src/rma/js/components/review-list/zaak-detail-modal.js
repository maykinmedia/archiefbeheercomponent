import React, { useState, useContext, useEffect } from "react";
import Modal from 'react-modal';

import {ConstantsContext} from "./context";
import {TextInput} from "../../forms/inputs";


const ZaakDetailModal = ({ modalIsOpen, setIsOpen, zaak, setSuggestion, comment, setComment}) => {

    const { zaakDetailUrl } = useContext(ConstantsContext);
    const closeModal = () => setIsOpen(false);
    const suggestClose = (suggestion) => {
        setSuggestion(suggestion);
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
            const fullUrl = `${zaakDetailUrl}?zaak_url=${zaak.url}`;
            window.fetch(fullUrl)
                .then(res => res.json())
                .then(
                    (result) => {
                        setIsLoaded(true);
                        setZaakDetail(result);
                    },
                    (error) => {
                        setIsLoaded(true);
                        setError(error);
                    }
                )
        }
    }, [modalIsOpen, isLoaded]);

    // rendered components


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
                                >Change
                                </button>
                                <button
                                    type="button"
                                    className="btn"
                                    onClick={(e) => suggestClose("remove")}
                                >Remove
                                </button>
                                <button
                                    type="button"
                                    className="btn"
                                    onClick={(e) => suggestClose("")}
                                >Approve
                                </button>
                            </div>

                        </>
                }
            </article>

        </Modal>
    );
}

export { ZaakDetailModal };
