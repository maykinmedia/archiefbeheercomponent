import React, {useEffect, useState} from "react";

import { ReviewItemForm } from "./review-item-form";
import { ManagementForm } from "../../forms/management-form";


const ReviewItemFormset = ({ itemsUrl }) => {
    const prefix = "item_reviews";

    // load list items
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([]);

    // fetch list items
    useEffect(() => {
        window.fetch(itemsUrl)
            .then(res => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setItems(result.items);

                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
    }, []);


    //set up forms
    const forms = items.map(
        (data, index) => <ReviewItemForm key={index} index={index} data={data} />
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
                prefix={ prefix}
                initial_forms="0"
                total_forms={ items.length }
                min_num_forms="0"
                max_num_forms="1000"
            />

            <table className="table">
                <thead>
                    <tr>
                        <th className="table__header">Identificatie</th>
                        <th className="table__header">Zaaktype</th>
                        <th className="table__header">Omschrijving</th>
                        <th className="table__header">Actie</th>
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
