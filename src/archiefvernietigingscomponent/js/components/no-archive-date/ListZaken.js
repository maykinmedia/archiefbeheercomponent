import React, {useState} from 'react';
import useAsync from 'react-use/esm/useAsync';
import PropTypes from 'prop-types';

import {get} from '../../utils/api';
import {ZakenTable} from '../destruction-list-create/zaken-table';
import ErrorMessage from '../ErrorMessage';
import ZaakIdentificatieFilter from './ZaakIdentificatieFilter';



const ListZaken = ({zakenUrl}) => {
    const [error, setError] = useState(null);
    const [zaken, setZaken] = useState([]);
    const [checkboxes, setCheckboxes] = useState([]);
    const [identificatieFilter, setIdentificatieFilter] = useState([]);

    // Fetch zaken
    const {loading} = useAsync( async () => {
        const response = await get(zakenUrl, {
            'archiefactiedatum__isnull': true,
            'einddatum__isnull': false,
            'sort_by_zaaktype': true
        });

        if (!response.ok) {
            setError(true);
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
                <aside className="destruction-create__filters filter-group">
                    <h2 className="section-title section-title--highlight">Filters</h2>
                    <div className="filter-group__item">
                        <label htmlFor={"id_zaaktypen"}>Zaak identificatie</label>
                        <ZaakIdentificatieFilter
                            zakenIdentificaties={zaken.map((zaak, index) => {
                                return zaak['identificatie']
                            })}
                            selected={identificatieFilter}
                            onChange={setIdentificatieFilter}
                        />
                    </div>
                </aside>
                <section className="destruction-create__zaken">
                    <h2 className="section-title section-title--highlight">Zaakdossiers</h2>
                    {
                        !error
                        ? (<ZakenTable
                            zaken={zaken.filter((zaak, index) => {
                                return (identificatieFilter.includes(zaak.identificatie) || !identificatieFilter.length);
                            })}
                            isLoaded={!loading}
                            error={error}
                            checkboxes={checkboxes}
                            setCheckboxes={setCheckboxes}
                            canUpdateZaak={true}
                        />)
                        : <ErrorMessage />
                    }
                </section>
            </div>
        </>
    );
};


ListZaken.propTypes = {
    zakenUrl: PropTypes.string.isRequired,
};


export default ListZaken;
