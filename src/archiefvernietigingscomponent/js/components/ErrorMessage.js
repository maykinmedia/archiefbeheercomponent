import React from 'react';
import PropTypes from 'prop-types';


const ErrorMessage = ({message}) => {
    const errorMessage = message || 'Er is een fout opgetreden. Probeer het later opnieuw.';
    return (
        <div className="error-message">
            <span className="material-icons">error_outline</span>{errorMessage}
        </div>
    )
};


ErrorMessage.propTypes = {
    message: PropTypes.string,
}


export default ErrorMessage;
