import React from "react";


const Input = (props) => {
    const { type, id, name, initial, classes, checked, onBlur, onChange } = props;
    return (
        <input
            type={type}
            name={name}
            id={id}
            defaultValue={initial || ""}
            checked={checked}
            className={classes}
            onBlur={ (event) => {
                if (onBlur) {
                    onBlur(event);
                }
            }}
            onChange={ (event) => {
                if (onChange) {
                    onChange(event);
                }
            }}
        ></input>
    );
};

const DateInput = (props) => {
    return <Input type="date" {...props} />;
};

const CheckboxInput = (props) => {
    return <Input type="checkbox" {...props} />;
};

export {Input, DateInput, CheckboxInput};
