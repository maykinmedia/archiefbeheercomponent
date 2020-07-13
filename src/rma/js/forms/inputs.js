import React from "react";


const Input = (props) => {
    const { type, id, name, initial, classes, checked, onBlur, onChange, required } = props;
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
            required={required || false }
        ></input>
    );
};


const TextInput = (props) => {
    return <Input type="text" {...props} />;
};


const DateInput = (props) => {
    return <Input type="date" {...props} />;
};

const CheckboxInput = (props) => {
    return <Input type="checkbox" {...props} />;
};

const RadioInput = (props) => {
    return <Input type="radio" {...props} />;
};

const HiddenInput = ({name, value}) => {
    return <input type="hidden" name={name} defaultValue={value} />
}


export {Input, TextInput, DateInput, CheckboxInput, RadioInput, HiddenInput};
