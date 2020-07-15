import React from 'react';


const Help = ({ helpText='', idForLabel='' }) => {
    if (!helpText) return null;
    let extraProps = {};
    if (idForLabel) {
        extraProps.id = `hint_${idForLabel}`;
    }
    return (
        <span className="input__hint" {...extraProps}>
            {helpText}
        </span>
    );
};


export { Help };
