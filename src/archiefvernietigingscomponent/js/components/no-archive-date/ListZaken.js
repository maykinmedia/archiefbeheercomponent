import React, {useState} from 'react';
import useAsync from 'react-use/esm/useAsync';
import PropTypes from 'prop-types';

import {get} from '../../utils/api';
import {ZakenTable} from '../destruction-list-create/zaken-table';



const ListZaken = ({zakenUrl}) => {
    const [error, setError] = useState(null);
    const [zaken, setZaken] = useState([]);
    const [checkboxes, setCheckboxes] = useState([]);

    // Fetch zaken
    const {loading} = useAsync( async () => {
        const response = await get(zakenUrl, {'archiefactiedatum__isnull': true, 'einddatum__isnull': false});

        if (!response.ok) {
            setError(response.data);
            return;
        }

        setZaken(response.data.zaken);
        const unselectedCheckboxes = response.data.zaken.filter(zaak => zaak.available).reduce((result, zaak) => {
            return {...result, [zaak.url]: false};
        }, {});
        setCheckboxes(unselectedCheckboxes);

    }, []);

    return (
        <>
            <header className="destruction-create__header">
                <h1 className="title destruction-create__title">Zaken zonder archiefactiedatum</h1>
            </header>
            <div className="destruction-create__content">
                <section className="destruction-create__zaken">
                    <h2 className="section-title section-title--highlight">Zaakdossiers</h2>
                    <ZakenTable
                        zaken={zaken}
                        isLoaded={!loading}
                        error={error}
                        checkboxes={checkboxes}
                        setCheckboxes={setCheckboxes}
                    />
                </section>
            </div>
        </>
    );
};


ListZaken.propTypes = {
    zakenUrl: PropTypes.string.isRequired,
};


export default ListZaken;
