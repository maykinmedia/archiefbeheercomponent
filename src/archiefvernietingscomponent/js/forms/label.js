import React from 'react';


const Label = ({label='', required=false, idForLabel=''}) => {
    if (!label) {
        return null;
    }

    let extraProps = {};
    if (idForLabel) {
        extraProps.htmlFor = idForLabel;
    }

    /* jshint ignore:start */
    return (
        <label className="input__label" {...extraProps}>
            { label }
            { required ? null : <span className="label label--optional">optioneel</span> }
        </label>
    );
    /* jshint ignore:end */
};


export { Label };
