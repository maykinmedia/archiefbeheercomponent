import React, { useState, useEffect } from "react";


const Input = (props) => {
    const { type, id, name, initial, classes } = props;
    const [value, setValue] = useState(initial || "");
    return (
        <input
            type={type}
            name={name}
            id={id}
            onChange={ (event) => {
                setValue(event.text);
            }}
            defaultValue={value}
            className={classes}
        ></input>
    );
};

const DateInput = (props) => {
    return <Input type="date" {...props} />;
};

export {Input, DateInput};
