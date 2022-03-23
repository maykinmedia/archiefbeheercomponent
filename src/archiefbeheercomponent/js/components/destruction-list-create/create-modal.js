import React, {useContext, useState} from "react";
import Modal from 'react-modal';

import { CsrfInput } from '../../forms/csrf';
import {CheckboxInput, HiddenInput, Input, TextInput} from '../../forms/inputs';
import {Label} from '../../forms/label';
import {ShortReviewZaaktypesContext} from './context';
import {SelectReviewers} from './Reviewer';


const CreateModal = ({ zaken, checkboxes, modalIsOpen, setIsOpen, url, csrftoken }) => {

    const selectedUrls = Object.keys(checkboxes).filter(url => checkboxes[url]);
    const selectedCount = selectedUrls.length;
    const [containsSensitiveInfo, setContainsSensitiveInfo] = useState(true);

    const areMultipleReviewersMandatory = () => {
        // Check if all URLs of the selected zaaktypes are in the list of zaaktypes that don't require a second reviewer
        const shortReviewZaaktypes = useContext(ShortReviewZaaktypesContext);

        for (const zaakUrl of selectedUrls) {
            const selectedZaakDetails = zaken.filter((zaak) => zaak.url === zaakUrl)[0];
            if ( !shortReviewZaaktypes.includes(selectedZaakDetails.zaaktype.url) ) return true;
        }

        return false;
    };

    return (
        <Modal isOpen={modalIsOpen} className="modal">
            <button onClick={() => setIsOpen(false)} className="modal__close btn">&times;</button>
            <h1 className="title modal__title">Vernietigingslijst starten - {selectedCount} zaken</h1>
            <form method="post" encType="multipart/form-data" action={url} className="form">
                <CsrfInput csrftoken={csrftoken}/>
                <Input
                    type="hidden"
                    id={"id_zaken"}
                    name={"zaken"}
                    initial={selectedUrls}
                />
                {/* Used to log the ID of the cases that are selected, so that the backend doesnt need to
                fetch the zaken again. */}
                <HiddenInput
                    name="zaken_identificaties"
                    id="id_zaken_identificaties"
                    value={zaken.filter(zaak => checkboxes[zaak.url]).map(zaak => zaak.identificatie)}
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
                        <CheckboxInput
                            name={"contains_sensitive_info"}
                            initial={true}
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

                <div className="form__field-group">
                    <SelectReviewers
                        multipleReviewersMandatory={areMultipleReviewersMandatory()}
                    />
                </div>

                <div className="form__submit-row">
                    <button type="submit" className="btn">Bevestig</button>
                </div>
            </form>
        </Modal>
    );
}

export { CreateModal };
