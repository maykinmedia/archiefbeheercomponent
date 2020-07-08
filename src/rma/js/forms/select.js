import React from 'react';

import {RadioInput} from "./inputs";


const SelectInput = (props) => {
    const { choices, name, id, classes, onChange, disabled, selected } = props;

    // const [selected, setSelected] = useState(initial);
    const options = choices.map(([value, label], index) => {
        return (
            <option key={index} value={value}>{label}</option>
        );
    });

    return (
        <select
            name={name}
            id={id}
            className={classes}
            disabled={!!disabled}
            value={selected}
            onChange={(event) => {
                // setSelected(event.target.value);
                if (onChange) {
                    onChange(event.target.value)
                }
            }}
        >
            { options }
        </select>
    );
};


const SelectMultipleInput = (props) => {
    const { choices, name, id, classes, onChange, size} = props;

    const options = choices.map(([value, label], index) => {
        return (
            <option key={index} value={value}>{label}</option>
        );
    });

    return (
        <select
            multiple={true}
            size={size}
            name={name}
            id={id}
            className={classes}
            onChange={(event) => {
                const selectedOptions = Array.from(
                    event.target.selectedOptions,
                    option => option.value
                    );
                onChange(selectedOptions);
            }}
        >
            { options }
        </select>
    );
};


const RadioSelect = (props) => {
    const { choices, name, onChange, initialValue } = props;

    const radios = choices.map( ([value, label], index) => {
        return (
            <li key={index}>
                <label>
                    <RadioInput
                        name={name}
                        initial={value}
                        label={label}
                        checked={value === initialValue}
                        onChange={ (event) => {
                            if (onChange) {
                                onChange(event.target.value);
                            }
                        }}
                    />
                    {label}
                </label>
            </li>
        );
    });

    return (
        <ul>
            { radios }
        </ul>
    )
};


export {SelectInput, SelectMultipleInput, RadioSelect};
