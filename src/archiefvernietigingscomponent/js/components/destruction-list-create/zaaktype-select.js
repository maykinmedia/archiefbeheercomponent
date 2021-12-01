import React, {useState, useEffect} from "react";
import { Collapse } from "react-collapse";

import {CheckboxInput} from "../../forms/inputs";


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


const ZaaktypeSelect = ({zaaktypen, selectedZaaktypen, setSelectedZaaktypen, checkboxName="zaaktype-item"}) => {
    const [selectedGroups, setSelectedGroups] = useState([]);
    const [expandedGroups, setExpandedGroups] = useState([]);

    const getInitialCheckedGroups = () => {
        const filledGroups = zaaktypen.filter((zaaktype) => {
            const zaaktypeVersions = zaaktype[1];

            for (var counter=0; counter<zaaktypeVersions.length; counter++){
                if (!selectedZaaktypen.includes(zaaktypeVersions[counter][0])) {
                    return false;
                }
            }

            return true;
        });

        return filledGroups.map((zaaktype) => zaaktype[0]);
    };

    useEffect(() => {
        const initiallySelectedGroups = getInitialCheckedGroups();
        setSelectedGroups(initiallySelectedGroups);
    }, []);

    const addZaak = (value) => add(value, selectedZaaktypen, setSelectedZaaktypen);
    const removeZaak = (value) => remove(value, selectedZaaktypen, setSelectedZaaktypen);

    const addGroup = (value) => add(value, selectedGroups, setSelectedGroups);
    const removeGroup = (value) => remove(value, selectedGroups, setSelectedGroups);

    const expand = (value) => add(value, expandedGroups, setExpandedGroups);
    const collapse = (value) => remove(value, expandedGroups, setExpandedGroups);

    const ZaaktypeItem = ({value, label, group}) => (
        <li>
            <div className="zaaktype-select__description">
                <CheckboxInput
                    initial={value}
                    name={checkboxName}
                    checked={selectedZaaktypen.includes(value)}
                    onChange={(event) => {
                        if (event.target.checked){
                            addZaak(value);
                        } else {
                            removeZaak(value);
                            removeGroup(group);
                        }
                    }}
                />
                <div className="zaaktype-select__label">{label}</div>
            </div>
        </li>
    );

    const groups = zaaktypen.map( ([description, choices], index) => {
        const buttonIcon = (expandedGroups.includes(description) ? "-" : "+");
        const choiceValues = choices.map(([value, label]) => value);

        const checkboxes = choices.map(([value, label]) => (
            <ZaaktypeItem key={value} value={value} label={label} group={description}/>
        ));

        return (
            <li key={index}>
                <div className="zaaktype-select__description">
                    <button
                        className="zaaktype-select__btn"
                        type="button"
                        onClick={(event) => {
                            const action = expandedGroups.includes(description) ? collapse : expand;
                            action(description);
                        }}
                    >{buttonIcon}
                    </button>
                        <CheckboxInput
                            initial={description}
                            name="zaaktype-group"
                            checked={selectedGroups.includes(description)}
                            onChange={(event) => {
                                if (event.target.checked) {
                                    addGroup(description);
                                    const newZaaktypenSet = new Set([...selectedZaaktypen, ...choiceValues]);
                                    setSelectedZaaktypen([...newZaaktypenSet]);
                                } else {
                                    removeGroup(description);
                                    const newZaaktypen = selectedZaaktypen.filter((value)=> !choiceValues.includes(value));
                                    setSelectedZaaktypen(newZaaktypen);
                                }
                            }}
                        />
                    <div className="zaaktype-select__label">{description}</div>
                </div>

                <Collapse isOpened={expandedGroups.includes(description)}>
                    <ul className="zaaktype-select__items">
                        {checkboxes}
                    </ul>
                </Collapse>
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
