import React from "react";

import {CheckboxInput} from "./inputs";


const ZaaktypeSelect = ({zaaktypen, selectedZaaktypen, setSelectedZaaktypen}) => {
        const groups = zaaktypen.map( ([description, choices], index) => {

            const checkboxes = choices.map(([value, label], index) => (
                <li key={index}>
                    <label>
                        <CheckboxInput
                            initial={value}
                            name="zaaktype-checkbox"
                            checked={selectedZaaktypen.includes(value)}
                            onChange={(event) => {
                                const shouldInclude = event.target.checked;
                                let newSelected = [...selectedZaaktypen];
                                if (shouldInclude && !newSelected.includes(value)) {
                                    newSelected.push(value);
                                } else if (!shouldInclude && newSelected.includes(value)) {
                                    newSelected = newSelected.filter(x => x !== value);
                                }
                                setSelectedZaaktypen(newSelected);
                            }}
                        />
                        {label}
                    </label>
                </li>
            ));

            return (
                <li key={index}>
                    <span>{`${description}:`}</span>
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
