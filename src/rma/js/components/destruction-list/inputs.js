import React from "react";


const Input = (props) => {
    const { type, id, name, initial, classes, onBlur, onChange } = props;
    return (
        <input
            type={type}
            name={name}
            id={id}
            onBlur={ (event) => {
                if (onBlur) {
                    onBlur(event.target.value);
                }
            }}
            onChange={ (event) => {
                if (onChange) {
                    onChange(event.target.value);
                }
            }}
            defaultValue={initial || ""}
            className={classes}
        ></input>
    );
};

const DateInput = (props) => {
    return <Input type="date" {...props} />;
};

export {Input, DateInput};
