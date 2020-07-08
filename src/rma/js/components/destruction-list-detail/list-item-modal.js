import React, {useContext, useState} from "react";
import Modal from 'react-modal';


const ListItemModal = ({modalIsOpen, setIsOpen, listItem, zaak}) => {
    const closeModal = () => setIsOpen(false);

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <article>
                <button onClick={closeModal} className="modal__close btn">&times;</button>
                <h1 className="title modal__title">{zaak.identificatie}</h1>
            </article>
        </Modal>
    );
};

export { ListItemModal };

