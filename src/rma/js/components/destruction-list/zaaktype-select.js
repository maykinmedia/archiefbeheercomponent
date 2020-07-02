import React from "react";

import {CheckboxInput} from "./inputs";


const ZaaktypeSelect = ({zaaktypen, selectedZaaktypen, setSelectedZaaktypen}) => {
    const add = (value) => {
        if (selectedZaaktypen.includes(value)) {
            return;
        }
        const newSelected = [...selectedZaaktypen];
        newSelected.push(value);
        setSelectedZaaktypen(newSelected);
    };

    const remove = (value) => {
        if (!selectedZaaktypen.includes(value)) {
            return;
        }
        const newSelected = selectedZaaktypen.filter(x => x !== value);
        setSelectedZaaktypen(newSelected);
    };

    const groups = zaaktypen.map( ([description, choices], index) => {

        const checkboxes = choices.map(([value, label], index) => (
            <li key={index}>
                <label>
                    <CheckboxInput
                        initial={value}
                        name="zaaktype-item"
                        checked={selectedZaaktypen.includes(value)}
                        onChange={(event) => {
                            const action = event.target.checked ? add: remove;
                            action(value);
                        }}
                    />
                    {label}
                </label>
            </li>
        ));

        return (
            <li key={index}>
                <label>
                    <CheckboxInput
                        initial={description}
                        name="zaaktype-group"
                        onChange={(event) => {
                            const action = event.target.checked ? add: remove;
                            choices.forEach(([value, label]) => action(value));
                        }}
                    />
                    {`${description}:`}
                </label>

                <ul>
                    {checkboxes}
                </ul>
            </li>
        );
    });

    return (
        <ul className="destruction-create__zaaktype">
            { groups }
        </ul>
    );
}


export { ZaaktypeSelect };
