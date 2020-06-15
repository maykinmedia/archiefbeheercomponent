import React from 'react';


const SelectInput = (props) => {
    const { choices, name, id, multiple, classes, onChange, size } = props;

    const options = choices.map(([value, label], index) => {
        return (
            <option key={index} value={value}>{label}</option>
        );
    });

    return (
        <select
            multiple={!!multiple}
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

export {SelectInput};
