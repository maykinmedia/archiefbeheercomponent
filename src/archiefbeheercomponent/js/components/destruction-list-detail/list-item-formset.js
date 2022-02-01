import React, {useContext, useState} from 'react';
import useAsync from 'react-use/esm/useAsync';
import PropTypes from 'prop-types';

import { ListItemForm } from './list-item-form';
import { ManagementForm } from '../../forms/management-form';
import { FormsetConfigContext } from './context';
import ErrorMessage from '../ErrorMessage';
import {Loader} from '../loader';
import {get} from '../../utils/api';


const ListItemFormset = ({itemsUrl}) => {
    const [items, setItems] = useState([]);
    const [error, setError] = useState(null);

    const formsetConfig = useContext(FormsetConfigContext);

    const {loading} = useAsync(async () => {
        const response = await get(itemsUrl);

        if (!response.ok) {
            setError(response.data);
            return;
        }

        if (response.data.error) {
            setError(response.data.error);
        } else {
            setItems(response.data.items);
        }
    }, []);

    if (error) {
        return (
            <section className="list-items">
                <h2 className="list-items__header section-title">Zaakdossiers</h2>
                <ErrorMessage message={error}/>
            </section>
        );
    }

    if (loading) {
        return (
            <section className="list-items">
                <h2 className="list-items__header section-title">Zaakdossiers</h2>
                <Loader/>
            </section>
        );
    }

    return (
        <section className="list-items">
            <h2 className="list-items__header section-title">Zaakdossiers</h2>

            <ManagementForm
                prefix={ formsetConfig.prefix }
                initial_forms={ formsetConfig.INITIAL_FORMS }
                total_forms={ items.length }
                min_num_forms={ formsetConfig.MIN_NUM_FORMS }
                max_num_forms={ formsetConfig.MAX_NUM_FORMS }
            />

            <table className="table">
                <thead>
                    <tr>
                        <th className="table__hidden">List item id</th>
                        <th className="table__header">Identificatie</th>
                        <th className="table__header">Zaaktype</th>
                        <th className="table__header" title="Zaak omschrijving">Omschrijving</th>
                        <th className="table__header">Looptijd</th>
                        <th className="table__header" title="Verantwoordelijke organisatie">VO</th>
                        <th className="table__header">Resultaattype</th>
                        <th className="table__header" title="Archiefactietermijn">Bewaartermijn</th>
                        <th className="table__header" title="Vernietigings-categorie selectielijst">VCS</th>
                        <th className="table__header" title="Relaties met andere zaken?">Relaties?</th>
                        <th className="table__header">Status</th>
                        <th className="table__header">Actie</th>
                        <th className="table__hidden">Archief</th>
                    </tr>
                </thead>
                <tbody>
                    {
                        items.map((data, index) => (
                            <ListItemForm
                                key={data.listItem.id}
                                index={index}
                                data={data}
                            />
                        ))
                    }
                </tbody>
            </table>
        </section>
    );

};


ListItemFormset.propTypes = {
    itemsUrl: PropTypes.string,
};


export { ListItemFormset };
