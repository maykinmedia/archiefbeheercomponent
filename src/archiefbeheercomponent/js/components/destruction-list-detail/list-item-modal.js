import React from 'react';
import Modal from 'react-modal';
import PropTypes from 'prop-types';

import {DateInput} from '../../forms/inputs';
import {RadioSelect} from '../../forms/select';
import {ARCHIEFNOMINATIE_CHOICES} from '../constants';


const ListItemModal = ({modalIsOpen, listItem, zaak, archiefnominatie, archiefactiedatum, onChange}) => {
    const archivingDetailsChanged = (
        archiefnominatie !== zaak.archiefnominatie || archiefactiedatum !== zaak.archiefactiedatum
    );

    return (
        <Modal isOpen={modalIsOpen} className="modal" bodyOpenClassName="modal-background__open">
            <article className="list-item-modal">
                <button
                    onClick={() => onChange({modalIsOpen: false})}
                    className="modal__close btn"
                >&times;</button>
                <h1 className="title modal__title">{zaak.identificatie}</h1>

                <div className="modal__section">
                    <section className="content-panel modal__item">
                        <h2 className="section-title section-title--highlight">Beoordeling</h2>

                        <h3>Opmerkingen</h3>
                        <p>
                            { listItem.review_text ? listItem.review_text : 'Geen opmerkingen'}
                        </p>
                    </section>
                    <section className="content-panel modal__item">
                        <h2 className="section-title section-title--highlight">Wijzigingen</h2>

                        <div className="list-item-modal__archiefnominatie">
                            <label><strong>Archiefnominatie</strong>
                            <RadioSelect
                                name="archiefnominatie"
                                choices={ARCHIEFNOMINATIE_CHOICES}
                                initialValue={archiefnominatie}
                                onChange={(e) => onChange({archiefnominatie: e.target.value})}
                            />
                        </label>
                        </div>

                        <div className="list-item-modal__archiefactiedatum">
                            <label><strong>Archiefactiedatum</strong>
                                <DateInput
                                    name="archiefactiedatum"
                                    initial={archiefactiedatum}
                                    onChange={(e) => onChange({archiefactiedatum: e.target.value})}
                                />
                            </label>
                        </div>
                    </section>
                </div>

                <div className="modal__buttons">
                    <button
                        onClick={(e) => {
                            const action = archivingDetailsChanged ? 'change_and_remove' : 'remove';
                            onChange({action: action, modalIsOpen: false});
                        }}
                        className="btn"
                    >Zaak uitzonderen
                    </button>

                    <button
                        onClick={(e) => {
                            onChange({
                                action: '',
                                archiefactiedatum: zaak.archiefactiedatum,
                                archiefnominatie: zaak.archiefnominatie,
                                modalIsOpen: false,
                            });
                        }}
                        className="btn"
                    >Zaak behouden
                    </button>
                </div>

            </article>
        </Modal>
    );
};


ListItemModal.propTypes = {
    modalIsOpen: PropTypes.bool.isRequired,
    listItem: PropTypes.object.isRequired,
    zaak: PropTypes.object.isRequired,
    archiefnominatie: PropTypes.string.isRequired,
    archiefactiedatum: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
}


export { ListItemModal };

