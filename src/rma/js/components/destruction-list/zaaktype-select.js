import React, {useState} from "react";

import {CheckboxInput} from "./inputs";


const add = (value, arr, setState) => {
    if (arr.includes(value)) {
        return;
    }
    const newArr = [...arr];
    newArr.push(value);

    setState(newArr);
};

const remove = (value, arr, setState) => {
    if (!arr.includes(value)) {
        return;
    }
    const newArr = arr.filter(x => x !== value);
    setState(newArr);
};


const ZaaktypeSelect = ({zaaktypen, selectedZaaktypen, setSelectedZaaktypen}) => {
    const [selectedGroups, setSelectedGroups] = useState([]);

    const addZaak = (value) => add(value, selectedZaaktypen, setSelectedZaaktypen);
    const removeZaak = (value) => remove(value, selectedZaaktypen, setSelectedZaaktypen);

    const addGroup = (value) => add(value, selectedGroups, setSelectedGroups);
    const removeGroup = (value) => remove(value, selectedGroups, setSelectedGroups);

    const groups = zaaktypen.map( ([description, choices], index) => {

        const checkboxes = choices.map(([value, label], index) => (
            <li key={index}>
                <label>
                    <CheckboxInput
                        initial={value}
                        name="zaaktype-item"
                        checked={selectedZaaktypen.includes(value)}
                        onChange={(event) => {
                            if (event.target.checked){
                                addZaak(value);
                            } else {
                                removeZaak(value);
                                removeGroup(description);
                            }
                        }}
                    />
                    {label}
                </label>
            </li>
        ));

        return (
            <li key={index}>
                <button type="button">+</button>
                <label>
                    <CheckboxInput
                        initial={description}
                        name="zaaktype-group"
                        checked={selectedGroups.includes(description)}
                        onChange={(event) => {
                            if (event.target.checked) {
                                addGroup(description);
                                choices.forEach(([value, label]) => addZaak(value));
                            } else {
                                removeGroup(description);
                                choices.forEach(([value, label]) => removeZaak(value));
                            }
                        }}
                    />
                    {`${description}:`}
                </label>

                <ul className="zaaktype-select__items">
                    {checkboxes}
                </ul>
            </li>
        );
    });

    return (
        <div className="zaaktype-select">
            <ul className="zaaktype-select__groups">
                { groups }
            </ul>
        </div>
    );
}


export { ZaaktypeSelect };
