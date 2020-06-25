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

    return (
        <>
            <h2 className="review-items__header section-title">Zaakdossiers</h2>
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
                        <th className="table__header">Item Id</th>
                        <th className="table__header">Zaak</th>
                        <th className="table__header">text</th>
                        <th className="table__header">Suggestion</th>
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
