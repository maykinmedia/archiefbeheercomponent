import React from 'react';


const SelectInput = (props) => {
    const { choices, name, id, multiple, classes } = props;

    const options = choices.map(([value, label], index) => {
        return (
            <option key={index} value={value}>{label}</option>
        );
    });

    return (
        <select
            multiple={!!multiple}
            name={name}
            id={id}
            className={classes}
        >
            { options }
        </select>
    );
};

export {SelectInput};
