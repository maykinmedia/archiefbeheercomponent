import React from 'react';


const SelectInput = (props) => {
    const { choices, name, id, classes, onChange, disabled } = props;

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
            onChange={(event) => {
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

export {SelectInput, SelectMultipleInput};
