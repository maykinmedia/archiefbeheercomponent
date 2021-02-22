import React, { useState } from "react";
import Modal from 'react-modal';

import { CsrfInput } from "../../forms/csrf";
import {CheckboxInput, Input, TextInput} from "../../forms/inputs";
import { SelectInput } from "../../forms/select";
import {Label} from "../../forms/label";


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

    const [reviewer1, setReviewer1] = useState('');
    const [reviewer2, setReviewer2] = useState('');

    // Sensitive information state
    const [containsSensitiveInfo, setContainsSensitiveInfo] = useState(true);

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <button onClick={closeModal} className="modal__close btn">&times;</button>
            <h1 className="title modal__title">Vernietigingslijst starten - {selectedCount} zaken</h1>
            <form method="post" encType="multipart/form-data" action={url} className="form">
                <CsrfInput csrftoken={csrftoken}/>
                <Input
                    type="hidden"
                    id={"id_zaken"}
                    name={"zaken"}
                    initial={selectedUrls}
                />

                <div className="form__field-group">
                    <TextInput
                        label="Naam"
                        id={"id_name"}
                        name={"name"}
                        required={true}
                        helpText="Geef de vernietigingslijst een herkenbare naam"
                    />

                    <div>
                        <SelectInput
                            name="reviewer_1"
                            selected={reviewer1}
                            label="Eerste reviewer"
                            helpText="Kies de eerste medewerker om de lijst te beoordelen"
                            choices={reviewers}
                            id={"id_reviewer_1"}
                            required={true}
                            onChange={ (value) => {
                                setReviewer1(value);
                                setDisable2(!value);
                                setReviewers2(changedReviewers2(value));
                            }}
                        />
                        { disable2 ? null :
                            <SelectInput
                                name={"reviewer_2"}
                                selected={reviewer2}
                                label="Tweede reviewer"
                                choices={reviewers2}
                                id={"id_reviewer_2"}
                                required={false}
                                onChange={ (value) => {
                                    setReviewer2(value);
                                }}
                            />
                        }
                    </div>
                </div>

                <div className="form__field-group">
                    <div>
                        <CheckboxInput
                            name={"contains_sensitive_info"}
                            checked={containsSensitiveInfo}
                            value={containsSensitiveInfo}
                            id={"id_contains_sensitive_info"}
                            onChange={(event) => {setContainsSensitiveInfo(event.target.checked);}}
                        />
                        <Label
                            label={"Bevat gevoelige gegevens"}
                            required={true}
                            idForLabel={"id_contains_sensitive_info"}
                        />
                    </div>
                </div>

                <div className="form__submit-row">
                    <button type="submit" className="btn">Bevestig</button>
                </div>
            </form>

        </Modal>
    );
}

export { CreateModal };
