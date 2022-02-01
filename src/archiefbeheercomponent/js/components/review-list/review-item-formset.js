import React, {useContext} from 'react';
import PropTypes from 'prop-types';

import { ConstantsContext } from './context';
import { ReviewItemForm } from './review-item-form';
import { ManagementForm } from '../../forms/management-form';
import ErrorMessage from '../ErrorMessage';
import {Loader} from '../loader';


const ReviewItemFormset = ({ error, isLoaded, items }) => {
    const { formsetConfig, showOptionalColumns } = useContext(ConstantsContext);

    if (error) {
        return <ErrorMessage message={error} />;
    }

    if (!isLoaded) {
        return <Loader/>;
    }

    return (
        <>
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
                        { showOptionalColumns === "True" && <th className="table__header">Omschrijving</th>}
                        <th className="table__header">Looptijd</th>
                        <th className="table__header" title="Verantwoordelijke organisatie">VO</th>
                        <th className="table__header">Resultaattype</th>
                        <th className="table__header" title="Archiefactietermijn">Bewaartermijn</th>
                        <th className="table__header" title="Vernietigings-categorie selectielijst">VCS</th>
                        { showOptionalColumns === "True" && <th className="table__header" title="Relaties met andere zaken?">Relaties?</th>}
                        <th className="table__header">Actie</th>
                        <th className="table__hidden">Comment</th>
                    </tr>
                </thead>
                <tbody>
                    {
                        items.map((data, index) => (
                            <ReviewItemForm
                                key={data.listItem.id}
                                index={index}
                                data={data}
                            />
                        ))
                    }
                </tbody>
            </table>
        </>
    );

};


ReviewItemFormset.propTypes = {
    error: PropTypes.string,
    isLoaded: PropTypes.bool,
    items: PropTypes.arrayOf(PropTypes.object),
};


export { ReviewItemFormset };
