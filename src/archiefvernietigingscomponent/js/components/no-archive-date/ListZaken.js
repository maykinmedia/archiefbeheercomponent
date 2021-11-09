import React from 'react';
import PropTypes from 'prop-types';


const ListZaken = ({zakenUrl}) => {

    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">Zaken zonder archiefactiedatum</h1>
            </header>
            <div className="destruction-create__content">
                <section className="destruction-create__zaken">
                    <h2 className="section-title section-title--highlight">Zaakdossiers</h2>

                </section>
            </div>
        </>
    );
};


ListZaken.propTypes = {
    zakenUrl: PropTypes.string.isRequired,
};


export default ListZaken;
