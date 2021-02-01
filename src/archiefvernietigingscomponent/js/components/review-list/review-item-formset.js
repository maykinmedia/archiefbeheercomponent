import React, {useContext} from "react";

import { ConstantsContext } from "./context";
import { ReviewItemForm } from "./review-item-form";
import { ManagementForm } from "../../forms/management-form";


const ReviewItemFormset = ({ error, isLoaded, items }) => {
    const { formsetConfig } = useContext(ConstantsContext);

    //set up forms
    const forms = items.map(
        (data, index) => <ReviewItemForm
            key={data.listItem.id}
            index={index}
            data={data}
        />
    );

    if (error) {
        return <div>Error in fetching zaken: {error.message}</div>;
    }

    if (!isLoaded) {
        return <div>Loading...</div>;
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
                        <th className="table__header">Omschrijving</th>
                        <th className="table__header">Actie</th>
                        <th className="table__hidden">Comment</th>
                    </tr>
                </thead>
                <tbody>
                    { forms }
                </tbody>
            </table>
        </>
    );

};


export { ReviewItemFormset };
