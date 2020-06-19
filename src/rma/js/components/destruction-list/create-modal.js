import React, { useState } from "react";
import Modal from 'react-modal';

import { CsrfInput } from "./csrf";
import { Input, TextInput } from "./inputs";
import { SelectInput } from "./select";


const CreateModal = ({ checkboxes, modalIsOpen, setIsOpen, reviewers, url, csrftoken }) => {

    const closeModal = () => setIsOpen(false);
    const selectedUrls = Object.keys(checkboxes).filter(url => checkboxes[url]);
    const selectedCount = selectedUrls.length;

    // reviewers
    const [disable2, setDisable2] = useState(true);
    const [reviewers2, setReviewers2] = useState(reviewers);
    const changedReviewers2 = ( choice ) => {
        if (choice) {
            return reviewers.filter(k => k[0].toString() !== choice.toString());
        } else {
            return [...reviewers];
        }
    };

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <button onClick={closeModal} className="modal__close btn">&times;</button>
            <h1 className="title modal__title">Vernietigingslijst starten - {selectedCount} zaken</h1>
            <form method="post" encType="multipart/form-data" action={url}>
                <section className="filter-group">
                    <CsrfInput csrftoken={csrftoken}/>

                    <Input
                        type="hidden"
                        id={"id_zaken"}
                        name={"zaken"}
                        initial={selectedUrls}
                    />

                    <div className="filter-group__item">
                        <label htmlFor={"id_name"}>Naam</label>
                        <TextInput
                            id={"id_name"}
                            name={"name"}
                            required={true}
                        />
                    </div>

                    <label>Review</label>
                    <ol>
                        <li className="filter-group__item">
                            <SelectInput
                                choices={reviewers}
                                name={"reviewer_1"}
                                id={"id_reviewer_1"}
                                onChange={value => {
                                    setDisable2(!value);
                                    setReviewers2(changedReviewers2(value));
                                }}
                            />
                        </li>
                        {disable2 ? null : <li className="filter-group__item">
                            <SelectInput
                                choices={reviewers2}
                                name={"reviewer_2"}
                                id={"id_reviewer_2"}
                            />
                        </li>}
                    </ol>

                </section>
                <button type="submit" className="btn">Bevestig</button>
            </form>

        </Modal>
    );
}

export { CreateModal };
