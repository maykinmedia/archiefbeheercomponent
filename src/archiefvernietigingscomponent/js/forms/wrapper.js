import React from 'react';


const ErrorList = ({ errors=[] }) => {
    return (
        <React.Fragment>
            { errors.map((error, index) => <div key={index} className="input__error">{ error }</div>) }
        </React.Fragment>
    );
};


const Wrapper = ({ errors=[], children }) => {
    const hasErrors = errors && errors.length > 0;
    const className = "input";
    if (hasErrors) {
        className += " input--invalid";
    }
    return (
        <div className={className}>
            {children}
        </div>
    );
};


export { ErrorList, Wrapper };
