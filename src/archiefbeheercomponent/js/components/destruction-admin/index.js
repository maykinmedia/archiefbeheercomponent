import React, {useState} from "react";
import ReactDOM from "react-dom";
import {jsonScriptToVar} from "../../utils";
import {ZaaktypeSelect} from "../destruction-list-create/zaaktype-select";


const SelectShortReviewZaaktypen = ({zaaktypeChoices, initialZaaktypes}) => {
    const [selectedZaaktypes, setSelectedZaaktypes] = useState(initialZaaktypes);

    return (
        <React.Fragment>
            <label htmlFor={"id_short_review_zaaktypes"}>Zaaktypen met verkort vernietigingsproces:</label>
            <ZaaktypeSelect
                zaaktypen={zaaktypeChoices}
                selectedZaaktypen={selectedZaaktypes}
                setSelectedZaaktypen={(selected) => {
                    setSelectedZaaktypes(selected);
                }}
                checkboxName='short_review_zaaktypes'
            />
        </React.Fragment>
    );
};


const mount = () => {
    const nodes = document.getElementsByClassName('field-short_review_zaaktypes');
    if (nodes.length === 0) return;

    const zaaktypeChoices = jsonScriptToVar('zaaktype-choices');
    const initialZaaktypes = jsonScriptToVar('initial-zaaktypes');

    const node = nodes[0];

    ReactDOM.render(
        <SelectShortReviewZaaktypen
            zaaktypeChoices={zaaktypeChoices}
            initialZaaktypes={initialZaaktypes}
        />,
        node
    );
};

mount();
