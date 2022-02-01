import React, {useContext, useState} from 'react';
import Modal from 'react-modal';
import {FormattedMessage} from 'react-intl';

import { CsrfInput } from '../../forms/csrf';
import {CheckboxInput, HiddenInput, Input, TextInput} from '../../forms/inputs';
import { SelectInput } from '../../forms/select';
import {Label} from '../../forms/label';
import {ShortReviewZaaktypesContext} from './context';



const CreateModal = ({ zaken, checkboxes, modalIsOpen, setIsOpen, reviewers, url, csrftoken }) => {

    const closeModal = () => setIsOpen(false);
    const selectedUrls = Object.keys(checkboxes).filter(url => checkboxes[url]);
    const selectedCount = selectedUrls.length;

    const isSecondReviewerMandatory = () => {
        // Check if all URLs of the selected zaaktypes are in the list of zaaktypes that don't require a second reviewer
        const shortReviewZaaktypes = useContext(ShortReviewZaaktypesContext);

        for (var counter=0; counter < selectedUrls.length; counter++) {
            const zaak_details = zaken.filter((zaak) => {
                return zaak.url === selectedUrls[counter];
            })[0];

            if (!shortReviewZaaktypes.includes(zaak_details.zaaktype.url)) {
                return true;
            }
        }
        return false;
    };

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
            <h1 className="title modal__title">
                <FormattedMessage
                    description="Header modal create destruction list"
                    defaultMessage="Create destruction list {numSelectedZaken, plural,
                        one {(1 case selected)}
                        other {({numSelectedZaken} cases selected)}
                    }"
                    values={{numSelectedZaken: selectedCount}}
                />
            </h1>
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
                        label={<FormattedMessage description="destruction list 'Name' field label" defaultMessage="Name" />}
                        id={"id_name"}
                        name={"name"}
                        required={true}
                        helpText={<FormattedMessage description="destruction list 'Name' field help text" defaultMessage="Give the destruction list a recognisable name" />}
                    />

                    <div>
                        <SelectInput
                            name="reviewer_1"
                            selected={reviewer1}
                            label={<FormattedMessage description="first reviewer" defaultMessage="First reviewer" />}
                            helpText={<FormattedMessage description="first reviewer helptext" defaultMessage="Choose the first employee who should review the destruction list" />}
                            choices={reviewers}
                            id={"id_reviewer_1"}
                            required={true}
                            onChange={ (value) => {
                                setReviewer1(value);
                                setDisable2(!value);
                                setReviewers2(changedReviewers2(value));
                            }}
                        />
                        <SelectInput
                            name={"reviewer_2"}
                            selected={reviewer2}
                            label={<FormattedMessage description="second reviewer" defaultMessage="Second reviewer" />}
                            helpText={<FormattedMessage description="second reviewer helptext" defaultMessage="Choose the second employee who should review the destruction list" />}
                            choices={reviewers2}
                            id={"id_reviewer_2"}
                            required={isSecondReviewerMandatory()}
                            disabled={disable2}
                            onChange={ (value) => {
                                setReviewer2(value);
                            }}
                        />
                    </div>
                </div>

                <div className="form__field-group">
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
                            label={<FormattedMessage defaultMessage="Contains sensitive information" description="Label checkbox" />}
                            required={true}
                            idForLabel={"id_contains_sensitive_info"}
                        />
                    </div>
                </div>

                <div className="form__submit-row">
                    <button type="submit" className="btn"><FormattedMessage defaultMessage="Confirm" description="Button 'confirm" /></button>
                </div>
            </form>

        </Modal>
    );
}

export { CreateModal };
